from __future__ import annotations

from itertools import product
import re
from typing import Any

PERMISSION_PROFILE = "happycodex-evaluator"
PROTOCOL_REVIEW_MODES = ("none", "focused_hardening", "exact_final")
CONVERGENCE_PHASES = (
    "implementation",
    "focused_hardening",
    "candidate_frozen",
    "exact_final",
    "closed",
)
PHASE_REVIEW_MODES = {
    "implementation": frozenset({"none"}),
    "focused_hardening": frozenset({"none", "focused_hardening"}),
    "candidate_frozen": frozenset({"none"}),
    "exact_final": frozenset({"exact_final"}),
    "closed": frozenset({"none"}),
}
PHASE_REVIEW_MODE = {
    phase: "|".join(mode for mode in PROTOCOL_REVIEW_MODES if mode in allowed_modes)
    for phase, allowed_modes in PHASE_REVIEW_MODES.items()
}
PHASE_REVIEW_MODE_TEXT = ", ".join(
    f"{phase}={review_mode}" for phase, review_mode in PHASE_REVIEW_MODE.items()
)
PERMISSION_VALUES = {
    "decision": frozenset({"continue", "stop_for_user", "complete", "incomplete"}),
    "qualifies": frozenset({True, False}),
    "execplan_condition": frozenset(
        {"not_required", "missing", "usable", "needs_amendment"}
    ),
    "protocol_may_product_write": frozenset({True, False}),
    "protocol_review_mode": frozenset(PROTOCOL_REVIEW_MODES),
    "protocol_may_complete": frozenset({True, False}),
}
RECOVERY_ACTIONS = (
    "ask_user",
    "create_execplan",
    "complete_boundary_union",
    "create_contract_freeze_revision",
    "observe_red",
    "implement",
    "repair",
    "run_checks",
    "reconciliation",
    "focused_review",
    "freeze_candidate",
    "exact_final_review",
    "release",
    "none",
    "unknown",
)
RECOVERY_PENDING_GATES = (
    "user_selection",
    "contract_freeze",
    "red_oracle",
    "product_edit",
    "checks",
    "family_hardening",
    "boundary_repair",
    "reconciliation",
    "focused_review",
    "candidate_freeze",
    "exact_final_review",
    "release",
)
RECOVERY_MANIFEST_PREFIX = "RECOVERY-MANIFEST-SHA256:"
RECOVERY_MANIFEST_PATTERN = re.compile(
    rf"^{re.escape(RECOVERY_MANIFEST_PREFIX)}([0-9a-f]{{64}})$"
)
NATIVE_TOOL_NAMES = ("apply_patch", "codex", "codex-linux-sandbox", "rg")
BASE_COMMAND_PATHS = ("/usr/local/bin", "/usr/bin", "/bin")
PARENT_CONTEXT_ENV = ("CODEX_REMOTE_PAYLOAD", "CODEX_THREAD_ID", "PWD", "OLDPWD")
PUBLIC_040_PACKAGE_ARTIFACT_SHA256 = (
    "ace7f39fd61341e5d4b1bc3b268fd89a1562acaaacb80d7456c2bb97fb9c497e"
)
PUBLIC_040_PACKAGE_SEMANTIC_SHA256 = (
    "c5030e99dd7cd1681148c069775671c5720bb8dd366930ff90f61cbc54cdfc05"
)
FILESYSTEM_ISOLATION_POLICY = {
    "mechanism": "codex-permission-profile",
    "profile": PERMISSION_PROFILE,
    "filesystem": "minimal-plus-current-workspace-and-native-tools",
    "default_access": "deny",
    "workspace": "read-only",
    "nonworkspace": "unreadable",
    "credential_file": "parent-only-command-denied",
    "native_tool_allowlist": NATIVE_TOOL_NAMES,
    "native_tools": "read-only",
    "home": "isolated",
    "parent_task_environment": "stripped",
    "command_environment": "inherit-none",
    "network": "disabled",
    "selection": "explicit-on-every-turn",
}
DISABLED_FEATURES = (
    "apps",
    "goals",
    "hooks",
    "memories",
    "remote_plugin",
    "multi_agent",
)
PERMISSION_FIELDS = frozenset(
    {
        "decision",
        "qualifies",
        "execplan_condition",
        "protocol_may_product_write",
        "protocol_review_mode",
        "protocol_may_complete",
    }
)
RECOVERY_GATE_FIELDS = frozenset(
    {
        "qualifies",
        "protocol_may_product_write",
        "protocol_review_mode",
        "protocol_may_complete",
    }
)
RECOVERY_STATE_FIELDS = frozenset(
    {
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
        "marker_ids",
    }
)


def identity_match_values(value: Any) -> frozenset[str]:
    """Return every stable identity spelling accepted by the protocol matcher."""
    folded = str(value).casefold()
    if not folded.strip():
        return frozenset()
    candidates = {folded}
    candidates.update(
        folded[index + 1 :]
        for index, character in enumerate(folded)
        if character in {":", "/"} and folded[index + 1 :]
    )
    return frozenset(candidates)


def is_nonblank_identity(value: Any) -> bool:
    """Return whether a raw identity can participate in protocol matching."""
    return isinstance(value, str) and bool(identity_match_values(value))


def classification_identity_keys(item: Any) -> frozenset[str]:
    """Project a raw classification or sanitized receipt to comparable identity keys."""
    if not isinstance(item, dict):
        return frozenset()
    identity = item.get("identity")
    if isinstance(identity, str):
        return identity_match_values(identity)
    digests = item.get("identity_match_sha256s")
    if isinstance(digests, list) and all(isinstance(value, str) for value in digests):
        return frozenset(digests)
    return frozenset()


def classifications_share_identity(left: Any, right: Any) -> bool:
    return bool(
        classification_identity_keys(left) & classification_identity_keys(right)
    )


def classification_identity_failures(items: Any, *, label: str) -> list[str]:
    """Reject blank or alias-equivalent identities across one classification array."""
    if not isinstance(items, list):
        return [f"invalid {label} classifications"]
    failures: list[str] = []
    seen: list[frozenset[str]] = []
    for item in items:
        keys = classification_identity_keys(item)
        nonblank = isinstance(item, dict) and (
            is_nonblank_identity(item.get("identity"))
            or item.get("identity_nonblank") is True
        )
        if not nonblank or not keys:
            failures.append(f"blank {label} identity")
            continue
        if any(keys & prior for prior in seen):
            suffix = "; multiple blocker classifications" if label == "blocker" else ""
            failures.append(f"duplicate {label} identity{suffix}")
        seen.append(keys)
    return failures


def has_distinct_identity_assignment(
    options: list[list[frozenset[str]]],
) -> bool:
    """Return whether each required item can use a non-equivalent stable identity."""

    def assign(position: int, used: frozenset[str]) -> bool:
        if position == len(options):
            return True
        return any(
            keys and not keys & used and assign(position + 1, used | keys)
            for keys in options[position]
        )

    return assign(0, frozenset())


def gate_projection(value: Any) -> dict[str, bool]:
    """Project raw gate text into the state facts retained by sanitized receipts."""
    gates = value if isinstance(value, list) else []
    normalized = [
        re.sub(r"[^a-z0-9]+", "_", gate.casefold()).strip("_")
        for gate in gates
        if isinstance(gate, str)
    ]
    return {
        "repair_gate_present": any(
            any(
                token in gate
                for token in (
                    "repair",
                    "red_oracle",
                    "product_edit",
                    "checks",
                    "family_hardening",
                    "boundary_repair",
                    "reconciliation",
                    "contract_freeze",
                    "candidate_freeze",
                )
            )
            for gate in normalized
        ),
        "user_gate_present": any(
            "user_selection" in gate or "ask_user" in gate or "user_decision" in gate
            for gate in normalized
        ),
        "focused_review_gate_present": any(
            "review" in gate
            and ("focused" in gate or "choke_point" in gate or "bypass" in gate)
            for gate in normalized
        ),
        "exact_final_review_gate_present": any(
            "review" in gate and "exact" in gate and "final" in gate
            for gate in normalized
        ),
    }


def recovery_manifest_projection(value: Any) -> dict[str, Any]:
    """Return the one content digest carried through existing recovery marker IDs."""
    markers = value.get("marker_ids", []) if isinstance(value, dict) else []
    candidates = [
        marker
        for marker in markers
        if isinstance(marker, str) and marker.startswith(RECOVERY_MANIFEST_PREFIX)
    ]
    match = (
        RECOVERY_MANIFEST_PATTERN.fullmatch(candidates[0])
        if len(candidates) == 1
        else None
    )
    return {
        "recovery_manifest_count": len(candidates),
        "recovery_manifest_sha256": match.group(1) if match else None,
    }


def recovery_summary_consistent(value: Any) -> bool:
    """Check marker and accepted-failure facts that receipts must bind explicitly."""
    if not isinstance(value, dict):
        return False
    markers = value.get("marker_ids")
    tests = value.get("tests")
    if (
        not isinstance(markers, list)
        or not all(isinstance(marker, str) and marker for marker in markers)
        or len(markers) != len(set(markers))
        or not isinstance(tests, dict)
    ):
        return False
    test_markers = tests.get("marker_ids")
    failed = tests.get("failed")
    accepted = tests.get("accepted_failures")
    return (
        isinstance(test_markers, list)
        and all(isinstance(marker, str) and marker for marker in test_markers)
        and len(test_markers) == len(set(test_markers))
        and set(test_markers).issubset(markers)
        and type(failed) is int
        and type(accepted) is int
        and 0 <= accepted <= failed
    )


def _gate_facts(value: dict[str, Any]) -> dict[str, bool]:
    facts = {
        field: value.get(field) is True
        for field in (
            "repair_gate_present",
            "user_gate_present",
            "focused_review_gate_present",
            "exact_final_review_gate_present",
        )
    }
    for source in (
        value.get("open_gates"),
        value.get("recovery_state", {}).get("pending_gates")
        if isinstance(value.get("recovery_state"), dict)
        else None,
    ):
        projected = gate_projection(source)
        facts = {field: facts[field] or projected[field] for field in facts}
    return facts


def protocol_state_failures(value: dict[str, Any]) -> list[str]:
    """Validate the central raw/result/receipt lifecycle boundary."""
    failures: list[str] = []
    decision = value.get("decision")
    execplan_condition = value.get("execplan_condition")
    may_write = value.get("protocol_may_product_write")
    review_mode = value.get("protocol_review_mode")
    may_complete = value.get("protocol_may_complete")
    completion_claimed = decision == "complete" or may_complete is True

    findings = value.get("finding_classifications", [])
    blockers = value.get("blocker_classifications", [])
    failures.extend(classification_identity_failures(findings, label="finding"))
    failures.extend(classification_identity_failures(blockers, label="blocker"))
    finding_items = findings if isinstance(findings, list) else []
    blocker_items = blockers if isinstance(blockers, list) else []
    for blocker in blocker_items:
        matches = sum(
            classifications_share_identity(finding, blocker)
            for finding in finding_items
        )
        if matches != 1:
            failures.append("blocker must match exactly one finding")

    if (decision == "complete") != (may_complete is True):
        failures.append("completion decision and permission disagree")
    if completion_claimed and may_write is True:
        failures.append("completion permits active product writes")
    if review_mode != "none" and may_write is True:
        failures.append("review mode and product write permission overlap")
    if completion_claimed and review_mode != "none":
        failures.append("completion must clear review mode to none")
    if decision == "stop_for_user":
        if may_write is True:
            failures.append("stop_for_user permits active product write")
        if review_mode != "none":
            failures.append("stop_for_user permits review mode")
    if execplan_condition in {"missing", "needs_amendment"}:
        if may_write is True:
            failures.append(
                f"{execplan_condition} ExecPlan permits active product write"
            )
        if review_mode != "none":
            failures.append(f"{execplan_condition} ExecPlan permits review")
        if completion_claimed:
            failures.append(f"{execplan_condition} ExecPlan permits completion")
    elif (
        review_mode in {"focused_hardening", "exact_final"}
        and execplan_condition != "usable"
    ):
        failures.append("review requires a usable ExecPlan")

    resolved = [
        item
        for item in finding_items
        if isinstance(item, dict) and item.get("state") == "resolved"
    ]
    blocking = [
        item
        for item in blocker_items
        if isinstance(item, dict) and item.get("blocking") is True
    ]
    if any(
        classifications_share_identity(finding, blocker)
        for finding in resolved
        for blocker in blocking
    ):
        failures.append("resolved finding is blocking")

    active_findings = [
        item
        for item in finding_items
        if isinstance(item, dict) and item.get("state") in {"candidate_new", "unknown"}
    ]
    recovery = value.get("recovery_state")
    gate_evidence_available = (
        "open_gates" in value
        or "open_gates_count" in value
        or isinstance(recovery, dict)
    )
    gates = _gate_facts(value)
    if review_mode in {"focused_hardening", "exact_final"}:
        if active_findings:
            failures.append(f"{review_mode} review mode has open finding")
        if blocking:
            failures.append(f"{review_mode} review mode has blocking blocker")
        if gates["repair_gate_present"]:
            failures.append(f"{review_mode} review mode has repair gate")
        if gates["user_gate_present"]:
            failures.append(f"{review_mode} review mode has user gate")
    if (
        review_mode == "focused_hardening"
        and gate_evidence_available
        and not gates["focused_review_gate_present"]
    ):
        failures.append("focused_hardening review mode lacks focused review gate")
    if (
        review_mode == "exact_final"
        and gate_evidence_available
        and not gates["exact_final_review_gate_present"]
    ):
        failures.append("exact_final review mode lacks exact-final review gate")

    if not isinstance(recovery, dict):
        return failures
    pending_gates = recovery.get("pending_gates")
    if recovery.get("next_action") == "ask_user" or (
        isinstance(pending_gates, list) and "user_selection" in pending_gates
    ):
        if may_write is True:
            failures.append(
                "pending recovery user selection permits active product write"
            )
        if review_mode != "none":
            failures.append("pending recovery user selection permits review")

    if recovery.get("writer") != "Root":
        failures.append("unknown writer in recovery")
    if recovery.get("worktree") == "unknown":
        failures.append("unknown worktree in recovery")
    for agent in (
        recovery.get("live_agents")
        if isinstance(recovery.get("live_agents"), list)
        else []
    ):
        if not isinstance(agent, dict):
            failures.append("invalid recovery agent")
        elif agent.get("status") == "missing":
            failures.append("missing agent in recovery")
        elif agent.get("status") != "terminal":
            failures.append("nonterminal recovery agent")
        elif agent.get("receipt_reproduced") is not True:
            failures.append("unreproduced recovery receipt")
    tests = recovery.get("tests")
    if isinstance(tests, dict):
        failed = tests.get("failed")
        accepted = tests.get("accepted_failures")
        if type(failed) is int and type(accepted) is int and failed > accepted:
            failures.append("unaccepted failure in recovery tests")

    manifest = (
        {
            "recovery_manifest_count": recovery.get("recovery_manifest_count"),
            "recovery_manifest_sha256": recovery.get("recovery_manifest_sha256"),
        }
        if "recovery_manifest_count" in recovery
        else recovery_manifest_projection(recovery)
    )
    if manifest["recovery_manifest_count"] == 0:
        failures.append("missing Recovery Manifest")
    elif manifest["recovery_manifest_count"] != 1:
        failures.append("duplicate Recovery Manifest")
    elif not isinstance(manifest["recovery_manifest_sha256"], str):
        failures.append("invalid Recovery Manifest")
    summary_consistent = recovery.get("summary_consistent")
    if summary_consistent is None:
        summary_consistent = recovery_summary_consistent(recovery)
    if summary_consistent is not True:
        failures.append("recovery summary mismatch")

    phase = recovery.get("milestone_phase")
    allowed_modes = PHASE_REVIEW_MODES.get(phase)
    if allowed_modes is None:
        failures.append(f"unknown convergence phase: {phase!r}")
        return failures
    if review_mode not in allowed_modes:
        failures.append(
            f"{phase} phase allows {PHASE_REVIEW_MODE[phase]} review mode, "
            f"got {review_mode!r}"
        )
    if phase in {"candidate_frozen", "exact_final", "closed"} and may_write is True:
        failures.append(f"{phase} phase permits active product writes")
    if (
        phase == "focused_hardening"
        and recovery.get("next_action") == "focused_review"
        and review_mode != "focused_hardening"
    ):
        failures.append("focused review is the sole next gate but review mode is none")
    if recovery.get("next_action") == "unknown":
        failures.append("unknown recovery next action")
    if recovery.get("next_action") == "none" and pending_gates:
        failures.append("recovery next action contradicts pending gates")
    if (
        recovery.get("next_action") not in {"none", "unknown"}
        and not pending_gates
        and phase != "closed"
    ):
        failures.append("recovery next action lacks a pending gate")
    if phase == "closed":
        if not completion_claimed:
            failures.append("closed phase requires completion")
    elif completion_claimed:
        failures.append(f"{phase} phase cannot claim completion")
    return failures


def expected_permission_failures(
    expected: dict[str, Any], *, recovery_state: dict[str, Any] | None = None
) -> list[str]:
    """Validate case-oracle permission options and every admitted state."""
    failures: list[str] = []
    options: dict[str, list[Any]] = {}
    for field, allowed in PERMISSION_VALUES.items():
        raw = expected.get(field)
        values = raw if isinstance(raw, list) else [raw]
        if (
            not values
            or len({(type(value), value) for value in values}) != len(values)
            or any(
                (
                    field
                    in {
                        "qualifies",
                        "protocol_may_product_write",
                        "protocol_may_complete",
                    }
                    and type(value) is not bool
                )
                or (
                    field
                    not in {
                        "qualifies",
                        "protocol_may_product_write",
                        "protocol_may_complete",
                    }
                    and type(value) is not str
                )
                or value not in allowed
                for value in values
            )
        ):
            failures.append(f"invalid {field}: {raw!r}")
        options[field] = values
    if failures:
        return failures
    fields = tuple(PERMISSION_VALUES)
    for values in product(*(options[field] for field in fields)):
        state = dict(zip(fields, values, strict=True))
        if recovery_state is not None:
            state["recovery_state"] = recovery_state
        failures.extend(protocol_state_failures(state))
    return sorted(set(failures))


BLOCKER_CLASSES = frozenset(
    {
        "original_goal",
        "frozen_acceptance",
        "safety_data_integrity",
        "production_condition",
        "exhaustive_claim",
    }
)
REQUIRED_TAGS = {
    "request-paraphrase",
    "unsupported-amendment",
    "uncertain-qualification",
    "midflight-escalation",
    "subthreshold-control",
    "clean-qualifying-control",
    "missed-boundary",
    "legacy-path",
    "missing-worker",
    "missing-deploy",
    "pre-freeze-compaction",
    "post-freeze-compaction",
    "lost-scout",
    "dirty-untracked",
    "baseline-failure",
    "authorized-rebaseline",
    "no-commit",
    "secret-output",
    "baseline-secret",
    "review-anchoring",
    "declared-dependency",
    "ledger-review-mismatch",
    "review-fallback",
    "goal-divergence",
    "submodule",
    "multi-repository",
    "omitted-diff-unit",
    "truncated-search",
    "persistence-transition",
    "concurrency-transition",
    "receipt-mismatch",
    "review-admin-cycle",
    "repository-policy",
    "exact-final-positive",
    "archive-positive",
    "no-commit-unselected",
}
IDENTITY_PROJECTION_TEXT = (
    "For an explicitly labeled material marker, locator, or digest, use the exact literal "
    "as the stable identity; a paraphrase is not equivalent. For a material path, create "
    "a distinct stable finding ID and copy the exact path into anchors."
)
DOMAIN_PROJECTION_TEXT = (
    "Use receipt only for an actual durable recovery/evidence/review receipt or an "
    "archive, checkpoint, ref, or digest artifact or recorded fact. A lifecycle marker "
    "that merely mentions review uses other; use secret only for secret findings and "
    "baseline_failure only for an explicitly recorded test/check failure identity."
)
STATE_PROJECTION_TEXT = (
    "Use resolved only for a closed finding that is therefore never blocking; use "
    "baseline_unchanged, candidate_new, or unknown for the corresponding current state."
)
ANCHOR_PROJECTION_TEXT = (
    "For every explicit marker, locator, digest, or recovery-affecting path, copy its "
    "exact literal into that finding's anchors; identity alone does not supply an anchor."
)
BLOCKER_PROJECTION_TEXT = (
    "Give every material completion blocker its own finding and reuse that finding "
    "identity in one blocker entry; a resolved finding is never blocking."
)
EXECPLAN_PROJECTION_TEXT = (
    "execplan_condition is usable when the durable plan exists and already authorizes "
    "the in-contract RED/repair; use needs_amendment only when the plan or contract "
    "itself must change before product work."
)
WRITE_PROJECTION_TEXT = (
    "In implementation or focused_hardening, protocol_may_product_write is true only "
    "for an authorized RED/repair or reconciliation while protocol_review_mode is none "
    "and no user or control gate intervenes; a completion blocker alone does not close "
    "permission."
)
EVALUATOR_CONTEXT = (
    "This invocation is an observational checkpoint only. "
    f"{EXECPLAN_PROJECTION_TEXT} {WRITE_PROJECTION_TEXT} Source and RED-test edits "
    "are product writes, while creating or amending an ExecPlan is not. Set review "
    "mode from write/reconciliation state and the sole next gate, constrained by "
    f"the lifecycle: {PHASE_REVIEW_MODE_TEXT}. "
    "invalid exact-final evidence returns to focused_hardening before a new final "
    "review; focused work may use repair history but cannot substitute for neutral "
    "final review. protocol_may_complete carries the completion gate. Put every material "
    "baseline/candidate finding with a nonblank stable identity in "
    "finding_classifications; identities must be unique after namespace-alias "
    f"projection within each finding or blocker array. {IDENTITY_PROJECTION_TEXT} "
    f"{DOMAIN_PROJECTION_TEXT} {STATE_PROJECTION_TEXT} {ANCHOR_PROJECTION_TEXT} "
    "Classify every explicitly "
    "labeled durable marker, including resolved positive controls, plus every staged, "
    "unstaged, and untracked path that affects recovery. "
    f"{BLOCKER_PROJECTION_TEXT} Classify blocker entries as original_goal, frozen_acceptance, "
    "safety_data_integrity, production_condition, or exhaustive_claim; a harmless "
    "observation is non-blocking. These fields do not describe or expand this read-only "
    "evaluator's permissions. Inspect only the current fixture "
    "repository; do not search for evaluator code, case definitions, or hidden oracles. "
    "Set recovery_state to null unless this is the runner's native compaction recovery "
    "control; there encode exact durable Git, plan, test, worktree, and agent facts. "
    "Copy pending_gates in checkpoint order without inferring downstream gates. "
    "live_agents contains only delegated scout, challenger, or reviewer facts, never "
    "the Root writer, and must include every delegated receipt named by the checkpoint. "
    "marker_ids contains only IDs explicitly labeled as durable recovery markers."
)
FIXED_GIT_DATE = "2000-01-01T00:00:00+00:00"
OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["continue", "stop_for_user", "complete", "incomplete"],
            "description": (
                "Coarse next control flow, not a synonym for task completeness; "
                "the protocol_may_* fields carry the permission gates."
            ),
        },
        "qualifies": {"type": "boolean"},
        "execplan_condition": {
            "type": "string",
            "enum": ["not_required", "missing", "usable", "needs_amendment"],
            "description": EXECPLAN_PROJECTION_TEXT,
        },
        "protocol_may_product_write": {
            "type": "boolean",
            "description": WRITE_PROJECTION_TEXT,
        },
        "protocol_review_mode": {
            "type": "string",
            "enum": list(PROTOCOL_REVIEW_MODES),
            "description": (
                "The sole review class authorized after applying findings, writes, "
                f"reconciliation, and next-gate facts: {PHASE_REVIEW_MODE_TEXT}. "
                "Invalid exact-final evidence returns to focused_hardening."
            ),
        },
        "protocol_may_complete": {
            "type": "boolean",
            "description": "Whether the protocol permits a completion claim.",
        },
        "finding_classifications": {
            "type": "array",
            "description": "Material baseline/candidate findings with stable IDs.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "identity": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 160,
                        "pattern": r"\S",
                        "description": IDENTITY_PROJECTION_TEXT,
                    },
                    "domain": {
                        "type": "string",
                        "enum": ["secret", "baseline_failure", "receipt", "other"],
                        "description": DOMAIN_PROJECTION_TEXT,
                    },
                    "state": {
                        "type": "string",
                        "enum": [
                            "baseline_unchanged",
                            "resolved",
                            "candidate_new",
                            "unknown",
                        ],
                        "description": STATE_PROJECTION_TEXT,
                    },
                    "anchors": {
                        "type": "array",
                        "description": ANCHOR_PROJECTION_TEXT,
                        "items": {"type": "string", "maxLength": 4_096},
                    },
                },
                "required": ["identity", "domain", "state", "anchors"],
            },
        },
        "blocker_classifications": {
            "type": "array",
            "description": BLOCKER_PROJECTION_TEXT,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "identity": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 160,
                        "pattern": r"\S",
                        "description": BLOCKER_PROJECTION_TEXT,
                    },
                    "class": {
                        "type": "string",
                        "enum": sorted(BLOCKER_CLASSES),
                    },
                    "blocking": {
                        "type": "boolean",
                        "description": BLOCKER_PROJECTION_TEXT,
                    },
                    "reason": {"type": "string", "maxLength": 240},
                },
                "required": ["identity", "class", "blocking", "reason"],
            },
        },
        "open_gates": {
            "type": "array",
            "items": {"type": "string", "maxLength": 240},
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string", "maxLength": 240},
        },
        "reason": {"type": "string", "maxLength": 1_200},
        "recovery_state": {
            "type": ["object", "null"],
            "additionalProperties": False,
            "properties": {
                "baseline_revision": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "baseline_tree": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "current_revision": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "current_tree": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "writer": {"type": "string", "enum": ["Root", "unknown"]},
                "milestone_phase": {
                    "type": "string",
                    "enum": list(CONVERGENCE_PHASES),
                },
                "next_action": {
                    "type": "string",
                    "enum": list(RECOVERY_ACTIONS),
                },
                "pending_gates": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": list(RECOVERY_PENDING_GATES),
                    },
                },
                "tests": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "passed": {"type": "integer", "minimum": 0},
                        "failed": {"type": "integer", "minimum": 0},
                        "accepted_failures": {
                            "type": "integer",
                            "minimum": 0,
                        },
                        "marker_ids": {
                            "type": "array",
                            "description": (
                                "Test IDs explicitly labeled as durable "
                                "recovery markers."
                            ),
                            "items": {"type": "string", "maxLength": 160},
                        },
                    },
                    "required": [
                        "passed",
                        "failed",
                        "accepted_failures",
                        "marker_ids",
                    ],
                },
                "worktree": {
                    "type": "string",
                    "enum": ["clean", "dirty", "unknown"],
                },
                "live_agents": {
                    "type": "array",
                    "description": (
                        "Every delegated scout, challenger, or reviewer "
                        "receipt named by the durable checkpoint; never Root."
                    ),
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string", "maxLength": 160},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "terminal", "missing"],
                            },
                            "receipt_reproduced": {"type": "boolean"},
                        },
                        "required": ["id", "status", "receipt_reproduced"],
                    },
                },
                "marker_ids": {
                    "type": "array",
                    "description": (
                        "Only IDs explicitly labeled as durable recovery "
                        "markers; order is not semantic."
                    ),
                    "items": {"type": "string", "maxLength": 160},
                },
            },
            "required": sorted(RECOVERY_STATE_FIELDS),
        },
    },
    "required": [
        "decision",
        "qualifies",
        "execplan_condition",
        "protocol_may_product_write",
        "protocol_review_mode",
        "protocol_may_complete",
        "finding_classifications",
        "blocker_classifications",
        "open_gates",
        "evidence",
        "reason",
        "recovery_state",
    ],
}
