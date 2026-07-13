from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/native-codex-loop/SKILL.md"
PACKETS = ROOT / "skills/native-codex-loop/references/task-packets.md"


class LeanPluginContractTests(unittest.TestCase):
    def test_plugin_is_a_skill_bundle_without_custom_runtime(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "native-codex-loop")
        self.assertEqual(manifest["skills"], "./skills/")
        for surface in ("hooks", "mcpServers", "apps"):
            self.assertNotIn(surface, manifest)

        tracked_runtime = subprocess.run(
            [
                "git",
                "ls-files",
                "--",
                "scripts",
                "docs/superpowers",
                "tests/test_review_runner.py",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(tracked_runtime, [])

    def test_skill_uses_native_state_and_one_root_writer(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        folded = " ".join(body.casefold().split())

        self.assertIn("name: native-codex-loop", frontmatter)
        self.assertIn("description: Use when", frontmatter)
        for phrase in (
            "root is the only writer",
            "user explicitly requests goal",
            "living evidence record",
            "do not require an execplan",
            "acceptance criteria",
            "git status",
            "git log",
            "focused tests",
            "full checks",
        ):
            self.assertIn(phrase, folded)

    def test_exploration_is_conditional_and_evidence_driven(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "independent unknowns",
            "read-only scouts",
            'fork_turns="none"',
            "complete task packet",
            "do not delegate implementation",
            "root reproduces",
            "unique evidence",
            "update the plan",
            "new boundary",
        ):
            self.assertIn(phrase, folded)

    def test_verification_uses_native_review_and_converges(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "red",
            "green",
            "git diff <task-baseline>..head",
            "staged, unstaged, and untracked",
            "selector flags",
            "independently reproduce",
            "one fresh re-review",
            "unresolved",
            "ask the user",
        ):
            self.assertIn(phrase, folded)

    def test_review_examples_respect_cli_selector_exclusivity(self) -> None:
        text = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        self.assertNotIn('codex review --base <task-baseline> "', text)
        self.assertNotIn('codex review --uncommitted "', text)
        self.assertNotIn('codex review "<factual brief', text)
        for phrase in (
            'codex review - < "$review_brief"',
            "codex review --base <task-baseline>",
            "codex review --uncommitted",
            "do not combine",
        ):
            self.assertIn(phrase, text)

    def test_review_brief_is_not_shell_interpolated(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "temporary review brief file",
            "do not interpolate its contents into a shell command",
            'codex review - < "$review_brief"',
        ):
            self.assertIn(phrase, folded)

    def test_review_normalizes_mixed_task_state(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "normalize task state before review",
            "commit all task changes",
            "worktree is clean",
            "if task commits and current task changes coexist",
            "both `git diff <task-baseline>..head` and the complete staged, unstaged, and untracked",
        ):
            self.assertIn(phrase, folded)

    def test_review_input_is_factual_fresh_and_writer_neutral(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "task, acceptance criteria, the complete diff",
            "verification evidence",
            "accepted baseline failures",
            "writer's implementation narrative",
            "self-review",
            "rebuttal",
            "preferred verdict",
        ):
            self.assertIn(phrase, folded)

    def test_scout_evidence_and_scope_changes_cannot_go_stale(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "record the inspected revision",
            "revision has changed",
            "re-confirm",
            "when the user changes scope",
            "update the working agreement and plan together",
            "mark affected prior evidence and decisions stale",
        ):
            self.assertIn(phrase, folded)

    def test_post_fix_rereview_preserves_complete_task_scope(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        clause = folded.split(
            "if confirmed findings changed the candidate", 1
        )[1].split("## completion gate", 1)[0]
        for phrase in (
            "complete updated diff",
            "commit all task changes",
            "git diff <task-baseline>..head",
            "same task baseline",
            "staged, unstaged, and untracked",
            "complete task must remain represented by current changes and any task checkpoints",
            "never advance the baseline or select only the post-review fix",
        ):
            self.assertIn(phrase, clause)

    def test_skill_does_not_recreate_the_retired_protocol(self) -> None:
        all_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL, PACKETS, ROOT / "README.md")
        ).casefold()
        for retired in (
            "review_runner",
            "hash chain",
            "successor receipt",
            "runner epoch",
            "bootstrap attestation",
            "retry challenge",
            "self-hosted review",
            "canonical series",
        ):
            self.assertNotIn(retired, all_text)

    def test_task_packet_is_complete_but_not_a_machine_protocol(self) -> None:
        text = PACKETS.read_text(encoding="utf-8")
        folded = text.casefold()
        for heading in (
            "## Scout task packet",
            "## Scout return",
            "## Root uptake",
        ):
            self.assertIn(heading, text)
        for field in (
            "decision",
            "question",
            "source of truth",
            "known facts",
            "exclusions",
            "write boundary",
            "deliverable",
            "verification",
            "stop condition",
            "unique evidence",
        ):
            self.assertIn(field, folded)
        self.assertIn("adapt the wording", folded)
        self.assertNotIn("sha256", folded)

    def test_bundle_stays_small_and_metadata_is_invocable(self) -> None:
        skill_lines = SKILL.read_text(encoding="utf-8").splitlines()
        packet_lines = PACKETS.read_text(encoding="utf-8").splitlines()
        readme_lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(skill_lines), 180)
        self.assertLessEqual(len(packet_lines), 100)
        self.assertLessEqual(len(readme_lines), 100)

        config = (ROOT / "skills/native-codex-loop/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$native-codex-loop", config)
        self.assertNotIn("dependencies:", config)


if __name__ == "__main__":
    unittest.main()
