"""Optional stateless review-admission guardrails for HappyCodex hooks."""
from __future__ import annotations

import json
import sys
from typing import Any


FULL_HISTORY = object()
EXACT_FINAL_NAMES = {
    "exact-final",
    "exact_final",
    "happycodex_exact_final",
    "plan_exact_final",
}

DENY_EXPLICIT_FULL_HISTORY = (
    "HappyCodex cannot combine an explicit agent_type with a full-history spawn. "
    "Use fork_turns=\"none\" for a custom fresh reviewer, a positive inherited-history "
    "fork for convergence review, or omit agent_type for a generic full-history fork."
)
EXACT_FINAL_ADMISSION = (
    "HappyCodex Exact-final admission: review one immutable consumer-native candidate "
    "identity as a fresh no-history reviewer. Return only GO or NOT_YET and echo that "
    "identity. Any candidate-byte change invalidates the verdict."
)
EXACT_FINAL_INHERITED = (
    "HappyCodex warning: this Exact-final spawn inherits history, so its output is "
    "convergence-only and has no terminal authority. A fresh no-history reviewer remains "
    "required for Exact-final admission."
)
EXACT_FINAL_FOLLOWUP = (
    "HappyCodex warning: interaction with an Exact-final handle is allowed, but any later "
    "output is convergence-only. A fresh no-history reviewer remains required for terminal "
    "admission."
)
COMPACT_REGROUND = (
    "HappyCodex re-ground: If a static ExecPlan governs this task, reread it completely; "
    "always rederive Goal, Outcome, scope, Git/index, candidate, and effect state; stop on "
    "identity, scope, index, effect, or trust drift."
)


def _specific(event: str, **values: str) -> dict[str, dict[str, str]]:
    return {"hookSpecificOutput": {"hookEventName": event, **values}}


def _exact_final(value: Any) -> bool:
    if type(value) is not str or not value.strip():
        return False
    leaf = value.strip().lower().rstrip("/").rsplit("/", 1)[-1]
    return leaf in EXACT_FINAL_NAMES


def _fork_kind(tool_input: dict[str, Any]) -> object | str | None:
    if "fork_turns" not in tool_input or tool_input["fork_turns"] == "all":
        return FULL_HISTORY
    value = tool_input["fork_turns"]
    if value == "none":
        return "none"
    if type(value) is str and value.isdigit() and int(value) > 0:
        return "positive"
    return None


def _nonempty_string(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def evaluate(payload: Any) -> dict[str, Any] | None:
    """Return one official hook response, or None to fail open."""
    if type(payload) is not dict:
        return None
    event = payload.get("hook_event_name")
    if event == "SessionStart":
        if payload.get("source") != "compact":
            return None
        return _specific("SessionStart", additionalContext=COMPACT_REGROUND)
    if event != "PreToolUse":
        return None

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if type(tool_name) is not str or type(tool_input) is not dict:
        return None

    if tool_name in {"Agent", "spawn_agent"}:
        if not all(
            _nonempty_string(tool_input.get(field))
            for field in ("task_name", "message")
        ):
            return None
        fork_kind = _fork_kind(tool_input)
        explicit_type = tool_input.get("agent_type")
        has_explicit_type = _nonempty_string(explicit_type)
        if has_explicit_type and fork_kind is FULL_HISTORY:
            return _specific(
                "PreToolUse",
                permissionDecision="deny",
                permissionDecisionReason=DENY_EXPLICIT_FULL_HISTORY,
            )
        exact_final = _exact_final(explicit_type) or _exact_final(tool_input.get("task_name"))
        if not exact_final or fork_kind is None:
            return None
        if fork_kind == "none":
            return _specific("PreToolUse", additionalContext=EXACT_FINAL_ADMISSION)
        return _specific("PreToolUse", additionalContext=EXACT_FINAL_INHERITED)

    if tool_name in {"followup_task", "send_message"}:
        if not all(
            _nonempty_string(tool_input.get(field))
            for field in ("target", "message")
        ):
            return None
        if _exact_final(tool_input.get("target")):
            return _specific("PreToolUse", additionalContext=EXACT_FINAL_FOLLOWUP)
        return None

    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        output = evaluate(payload)
        if output is not None:
            sys.stdout.write(json.dumps(output, separators=(",", ":")))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
