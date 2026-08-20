from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from hooks.session_firewall import evaluate


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "hooks/session_firewall.py"


def pretool(tool_name: str, tool_input: object) -> dict[str, object]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "transcript_path": "/must/not/be/read",
        "cwd": "/must/not/be-inspected",
    }


class SessionFirewallLogicTests(unittest.TestCase):
    def test_explicit_agent_type_with_full_history_is_denied(self):
        for agent_type in ("happycodex_exact_final", "custom_review"):
            for fork_turns in (None, "all"):
                tool_input = {
                    "task_name": "review",
                    "message": "review",
                    "agent_type": agent_type,
                }
                if fork_turns is not None:
                    tool_input["fork_turns"] = fork_turns
                output = evaluate(pretool("spawn_agent", tool_input))
                specific = output["hookSpecificOutput"]
                self.assertEqual(specific["hookEventName"], "PreToolUse")
                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertIn("explicit agent_type", specific["permissionDecisionReason"])

    def test_generic_full_history_without_agent_type_is_unaffected(self):
        self.assertIsNone(evaluate(pretool("spawn_agent", {
            "task_name": "reader", "message": "read", "fork_turns": "all",
        })))

    def test_exact_final_positive_history_is_allowed_but_convergence_only(self):
        output = evaluate(pretool("spawn_agent", {
            "task_name": "plan_exact_final",
            "message": "review",
            "agent_type": "happycodex_exact_final",
            "fork_turns": "3",
        }))
        specific = output["hookSpecificOutput"]
        self.assertEqual(set(specific), {"hookEventName", "additionalContext"})
        self.assertIn("convergence-only", specific["additionalContext"])
        self.assertIn("fresh no-history reviewer", specific["additionalContext"])

    def test_exact_final_no_history_gets_terminal_admission_context(self):
        output = evaluate(pretool("Agent", {
            "task_name": "exact-final",
            "message": "review",
            "agent_type": "exact_final",
            "fork_turns": "none",
        }))
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("one immutable consumer-native candidate identity", context)
        self.assertIn("full frozen bytes of any governing ExecPlan in a single request", context)
        self.assertIn("candidate or plan byte change", context)
        self.assertIn("GO or NOT_YET", context)
        self.assertIn("echo", context)

    def test_exact_final_followup_and_message_are_allowed_but_downgraded(self):
        for tool_name in ("followup_task", "send_message"):
            output = evaluate(pretool(tool_name, {
                "target": "/root/plan_exact_final", "message": "one more thought",
            }))
            specific = output["hookSpecificOutput"]
            self.assertEqual(set(specific), {"hookEventName", "additionalContext"})
            self.assertIn("convergence-only", specific["additionalContext"])
            self.assertIn("fresh no-history reviewer", specific["additionalContext"])

    def test_unrelated_followup_and_interrupt_are_unaffected(self):
        self.assertIsNone(evaluate(pretool("followup_task", {
            "target": "/root/explorer", "message": "continue",
        })))
        self.assertIsNone(evaluate(pretool("interrupt_agent", {
            "target": "/root/plan_exact_final",
        })))

    def test_compact_session_gets_concise_regrounding_context(self):
        output = evaluate({
            "hook_event_name": "SessionStart",
            "source": "compact",
            "transcript_path": "/must/not/be/read",
            "cwd": "/must/not/be-inspected",
        })
        specific = output["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "SessionStart")
        self.assertIn(
            "If a task-local ExecPlan governs this task, reread it completely",
            specific["additionalContext"],
        )
        self.assertIn("always rederive Goal", specific["additionalContext"])
        self.assertLess(len(specific["additionalContext"]), 500)

    def test_malformed_and_unknown_inputs_fail_open(self):
        for payload in (
            None,
            [],
            {},
            {"hook_event_name": "Unknown"},
            pretool("unknown_tool", {}),
            pretool("spawn_agent", "not-an-object"),
            pretool("spawn_agent", {"agent_type": "exact-final"}),
            pretool("followup_task", {"target": "/root/plan_exact_final"}),
        ):
            self.assertIsNone(evaluate(payload))


class SessionFirewallProcessAndConfigTests(unittest.TestCase):
    def run_script(self, raw: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            input=raw,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_subprocess_emits_official_json_and_fails_open(self):
        denied = self.run_script(json.dumps(pretool("spawn_agent", {
            "task_name": "review", "message": "review", "agent_type": "exact-final",
        })))
        self.assertEqual(denied.returncode, 0)
        self.assertEqual(
            json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        for raw in ("{", "[]", json.dumps({"hook_event_name": "Unknown"})):
            completed = self.run_script(raw)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr, "")

    def test_default_plugin_hook_config_and_commands(self):
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertNotIn("hooks", manifest)
        config = json.loads((ROOT / "hooks/hooks.json").read_text())
        self.assertEqual(set(config), {"description", "hooks"})
        self.assertEqual(set(config["hooks"]), {"PreToolUse", "SessionStart"})
        pretool_group = config["hooks"]["PreToolUse"][0]
        self.assertEqual(
            pretool_group["matcher"],
            "^(Agent|spawn_agent|followup_task|send_message)$",
        )
        self.assertEqual(config["hooks"]["SessionStart"][0]["matcher"], "^compact$")
        for group in config["hooks"].values():
            handler = group[0]["hooks"][0]
            self.assertEqual(handler["type"], "command")
            self.assertIn('$PLUGIN_ROOT/hooks/session_firewall.py', handler["command"])
            self.assertIn("%PLUGIN_ROOT%", handler["commandWindows"])


if __name__ == "__main__":
    unittest.main()
