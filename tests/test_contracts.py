from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts import review_runner


ROOT = Path(__file__).resolve().parents[1]


class ArtifactContractTests(unittest.TestCase):
    def test_red_baseline_receipt_is_immutable_and_meaningful(self) -> None:
        fixture = json.loads(
            (ROOT / "tests/fixtures/storyboard-red-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        report = Path(fixture["source_report"])
        self.assertEqual(
            hashlib.sha256(report.read_bytes()).hexdigest(),
            fixture["source_report_sha256"],
        )
        self.assertEqual(fixture["codex_native_agent_calls"], 0)
        self.assertEqual(len(fixture["missed_seams"]), 2)

    def test_plugin_manifest_has_only_v1_surfaces(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "native-codex-loop")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertFalse((ROOT / "hooks").exists())
        self.assertFalse((ROOT / ".mcp.json").exists())

    def test_v1_uses_isolated_review_process_not_broken_custom_agent_routing(
        self,
    ) -> None:
        self.assertFalse((ROOT / "assets/agents/native-codex-reviewer.toml").exists())
        self.assertFalse((ROOT / "scripts/preflight.py").exists())
        self.assertFalse((ROOT / "tests/test_preflight.py").exists())
        self.assertEqual(review_runner.MODEL, "gpt-5.6-sol")
        self.assertEqual(review_runner.EFFORT, "max")
        self.assertEqual(review_runner.SANDBOX, "read-only")

        command = review_runner._command(Path("codex"), Path("/tmp/review"), "base")
        rendered = " ".join(command)
        for phrase in (
            "exec review",
            'model_reasoning_effort="max"',
            'approval_policy="never"',
            'web_search="disabled"',
            "--ignore-rules",
        ):
            self.assertIn(phrase, rendered)
        self.assertNotIn("--ignore-user-config", command)
        self.assertNotEqual(command[-1], "-")
        profile = review_runner._profile_bytes("packet", Path("/runtime/bin")).decode()
        for phrase in (
            'default_permissions = "native-review"',
            "allow_login_shell = false",
            'inherit = "none"',
            '":minimal" = "read"',
            '":workspace_roots"',
            "[permissions.native-review.network]",
        ):
            self.assertIn(phrase, profile)
        for feature in ("plugins", "apps", "hooks", "multi_agent", "browser_use"):
            self.assertIn(f"--disable {feature}", rendered)

    def test_skill_metadata_is_trigger_only_and_body_has_completion_gate(self) -> None:
        skill_path = ROOT / "skills/native-codex-loop/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        self.assertIn("name: native-codex-loop", frontmatter)
        self.assertIn("description: Use when", frontmatter)
        for shortcut in ("reviewer", "Goal +", "root writer"):
            self.assertNotIn(shortcut, frontmatter)
        required = (
            "only writer",
            'fork_turns="none"',
            "acceptance criteria",
            "review_runner.py",
            "canonical series",
            "receipt.json",
            "review.md",
            "independently reproduce",
            "update_goal",
            "two review invocations",
            "references/packets.md",
        )
        for phrase in required:
            self.assertIn(phrase, body)
        self.assertNotIn("native_codex_reviewer", body)

    def test_packet_reference_defines_complete_dispatch_and_review_shapes(self) -> None:
        packets = (ROOT / "skills/native-codex-loop/references/packets.md").read_text(
            encoding="utf-8"
        )
        for heading in (
            "## Delegation packet",
            "## Review packet",
            "## Finding disposition",
        ):
            self.assertIn(heading, packets)
        for field in (
            "Objective",
            "Source of truth",
            "Write boundary",
            "Output contract",
            "Base commit",
            "Head commit",
            "Verification receipt",
            "Reproduction",
        ):
            self.assertIn(field, packets)


if __name__ == "__main__":
    unittest.main()
