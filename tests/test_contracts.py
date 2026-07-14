from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/happycodex/SKILL.md"
PACKETS = ROOT / "skills/happycodex/references/task-packets.md"


class HappyCodexContractTests(unittest.TestCase):
    def test_plugin_is_a_skill_bundle_without_custom_runtime(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "happycodex")
        self.assertEqual(manifest["skills"], "./skills/")
        for surface in ("hooks", "mcpServers", "apps"):
            self.assertNotIn(surface, manifest)

        tracked_files = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(
            set(tracked_files),
            {
                ".codex-plugin/plugin.json",
                ".gitignore",
                "README.md",
                "skills/happycodex/SKILL.md",
                "skills/happycodex/agents/openai.yaml",
                "skills/happycodex/references/task-packets.md",
                "tests/test_contracts.py",
            },
        )

    def test_skill_uses_native_state_and_one_root_writer(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        folded = " ".join(body.casefold().split())

        self.assertIn("name: happycodex", frontmatter)
        self.assertIn("description: Use for", frontmatter)
        for phrase in (
            "root is the only writer",
            "user explicitly requests goal",
            "living evidence record",
            "immutable task baseline",
            "full starting commit oid",
            "before any task edit",
            "never advance it",
            "acceptance criteria",
            "git status",
            "git log",
            "focused tests",
            "full checks",
            "preserved pre-existing non-task changes",
            "ownership and review exclusion",
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
            "root alone edits, commits, and integrates",
            "root reproduces",
            "unique lens",
            "update the plan",
            "newly exposed independent boundary",
        ):
            self.assertIn(phrase, folded)

    def test_verification_uses_native_review_and_converges(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "create the smallest meaningful red oracle",
            "make the smallest change that reaches green",
            "git diff <task-baseline>..head",
            "staged, unstaged, and untracked",
            "selector flags",
            "independently reproduce",
            "at most one fresh review",
            "unresolved",
            "ask the user",
        ):
            self.assertIn(phrase, folded)

    def test_native_review_prefers_sol_max_without_unbounded_escalation(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            'review_model="gpt-5.6-sol"',
            'model_reasoning_effort="max"',
            "at or below `max`",
            "never silently downgrade",
            "`ultra` requires explicit user authorization",
            "record the requested configuration and any invocation-reported model, effort, fallback, or reroute",
            "every review and re-review passes the resolved model and effort through both `-c` overrides",
        ):
            self.assertIn(phrase, folded)
        self.assertNotIn(
            "strongest native review setting authorized by the task",
            folded,
        )

    def test_every_review_uses_a_factual_stdin_brief(self) -> None:
        text = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        self.assertNotIn("codex review --base", text)
        self.assertNotIn("codex review --uncommitted", text)
        self.assertNotIn("codex review --commit", text)
        self.assertNotIn('codex review "<factual brief', text)
        for phrase in (
            'codex review -c \'review_model="gpt-5.6-sol"\' -c \'model_reasoning_effort="max"\' - < "$review_brief"',
            "every review invocation",
            "factual brief",
            "do not combine",
        ):
            self.assertIn(phrase, text)

    def test_review_brief_is_not_shell_interpolated(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "temporary review brief file",
            "outside the repository",
            "remove it afterward",
            "never shell-interpolate its contents",
            'codex review -c \'review_model="gpt-5.6-sol"\' -c \'model_reasoning_effort="max"\' - < "$review_brief"',
        ):
            self.assertIn(phrase, folded)

    def test_review_normalizes_mixed_task_state(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "normalize task state before review",
            "prefer a task-only commit",
            "git diff <task-baseline>..head",
            "every task-owned staged, unstaged, and untracked path",
            "recorded non-task exclusions",
            "commit or isolate when separation is ambiguous",
        ):
            self.assertIn(phrase, folded)

    def test_review_input_is_factual_fresh_and_writer_neutral(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        for phrase in (
            "task, acceptance criteria",
            "complete diff scope",
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
            "exact inspected snapshot",
            "candidate changed",
            "revalidate",
            "when the user changes scope",
            "update the working agreement and plan together",
            "mark affected criteria, evidence, and decisions stale",
        ):
            self.assertIn(phrase, folded)

    def test_post_fix_rereview_preserves_complete_task_scope(self) -> None:
        folded = " ".join(
            SKILL.read_text(encoding="utf-8").casefold().split()
        )
        clause = folded.split(
            "if confirmed fixes change the candidate", 1
        )[1].split("## completion gate", 1)[0]
        for phrase in (
            "same complete-scope, immutable-baseline, factual-brief, and resolved model/effort contract",
            "never review only the fix",
            "do not run a third review in this loop",
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

        config = (ROOT / "skills/happycodex/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$happycodex", config)
        self.assertNotIn("dependencies:", config)

    def test_retired_brand_is_absent_from_tracked_content(self) -> None:
        retired_slug = "-".join(("native", "codex", "loop"))
        retired_title = " ".join(("native", "codex", "loop"))
        tracked_files = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        tracked_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in tracked_files
        ).casefold()
        self.assertNotIn(retired_slug, tracked_text)
        self.assertNotIn(retired_title, tracked_text)


if __name__ == "__main__":
    unittest.main()
