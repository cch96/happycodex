from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/happycodex/SKILL.md"
PACKETS = ROOT / "skills/happycodex/references/task-packets.md"
README = ROOT / "README.md"


def folded(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").casefold().split())


class HappyCodexContractTests(unittest.TestCase):
    def test_plugin_is_a_small_skill_bundle_without_custom_runtime(self) -> None:
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
        body_folded = " ".join(body.casefold().split())

        self.assertIn("name: happycodex", frontmatter)
        self.assertIn("description: Use for", frontmatter)
        for phrase in (
            "root is the only writer",
            "user explicitly requests goal",
            "immutable task baseline",
            "acceptance criteria",
            "accepted baseline failures",
            "preserved pre-existing",
            "scope changes",
        ):
            self.assertIn(phrase, body_folded)

    def test_exploration_requires_coverage_without_scheduling_native_agents(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "trace the primary contract",
            "adversarial compatibility",
            "residual consumers",
            "the root decides whether to investigate directly or delegate",
            "do not target an agent count",
            "parallelize only questions that are independent",
            "named decision or verification gate",
            'fork_turns="none"',
            "root reproduces",
        ):
            self.assertIn(phrase, text)

        for retired in (
            "one to three direct read-only scouts",
            "initial scout lens",
            "plan challenger",
            "plan challenge adaptation",
        ):
            self.assertNotIn(retired, text)

    def test_implementation_is_evidence_driven(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "smallest meaningful red oracle",
            "red is unsafe, impractical, or lower-signal",
            "smallest change that reaches green",
            "focused tests",
            "required full checks",
            "never weaken acceptance criteria",
        ):
            self.assertIn(phrase, text)

    def test_native_review_is_fresh_complete_and_bounded(self) -> None:
        text = folded(SKILL)
        for phrase in (
            'review_model="gpt-5.6-sol"',
            'model_reasoning_effort="max"',
            "complete task diff",
            "immutable baseline",
            "verification evidence",
            "accepted baseline failures",
            "writer's implementation narrative",
            "independently reproduce",
            "at most one fresh re-review",
            "literal zero-finding result is unnecessary",
            "normalize task state before review",
            "prefer a task-only commit",
            "git diff <task-baseline>..head",
            "if a task-only commit is not used",
            "task-owned staged, unstaged, and untracked",
            "list task-owned untracked paths explicitly",
        ):
            self.assertIn(phrase, text)
        self.assertIn("`ultra` requires explicit user authorization", text)

    def test_rereview_is_unanchored_to_the_previous_review(self) -> None:
        text = folded(SKILL)
        clause = text.split("at most one fresh re-review", 1)[1].split(
            "## completion gate", 1
        )[0]
        for phrase in (
            "same immutable baseline",
            "complete current diff",
            "current verification evidence",
            "prior findings, dispositions, and repair narrative",
            "never review only the fix",
            "must run that one fresh re-review",
            "if that re-review reports a confirmed or unresolved material defect",
            "stop and report without changing the candidate",
            "newly authorized review cycle",
        ):
            self.assertIn(phrase, clause)

    def test_recovery_and_completion_reconcile_durable_evidence(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "after resume or compaction",
            "git status",
            "git log",
            "task diff",
            "avoid repeating completed",
            "material state or ownership",
            "every acceptance criterion maps to behavior or reproducible evidence",
            "scouts and worktrees are accounted for",
        ):
            self.assertIn(phrase, text)

    def test_task_packet_is_compact_and_evidence_oriented(self) -> None:
        text = PACKETS.read_text(encoding="utf-8")
        packet = folded(PACKETS)
        for heading in ("## Task packet", "## Scout return", "## Root uptake"):
            self.assertIn(heading, text)
        for phrase in (
            "named decision or verification gate",
            "one bounded question",
            "exact inspected snapshot",
            "known facts and exclusions",
            "read-only",
            "unique evidence",
            "remaining uncertainty",
            "root reproduction",
            "freshness",
        ):
            self.assertIn(phrase, packet)
        self.assertNotIn("plan challenge", packet)
        self.assertNotIn("sha256", packet)

    def test_bundle_stays_concise_and_metadata_matches_the_workflow(self) -> None:
        self.assertLessEqual(len(SKILL.read_text(encoding="utf-8").splitlines()), 130)
        self.assertLessEqual(len(PACKETS.read_text(encoding="utf-8").splitlines()), 55)
        self.assertLessEqual(len(README.read_text(encoding="utf-8").splitlines()), 80)

        config = (ROOT / "skills/happycodex/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$happycodex", config)
        self.assertIn("acceptance evidence", config)
        self.assertIn("native review", config)
        self.assertNotIn("dependencies:", config)

        manifest = folded(ROOT / ".codex-plugin/plugin.json")
        self.assertIn("acceptance evidence", manifest)
        self.assertIn("native review", manifest)
        self.assertIn("immutable task baseline", manifest)
        self.assertNotIn("immutable task scope", manifest)
        self.assertNotIn("dependency-aware read-only scouts", manifest)

    def test_retired_protocol_and_brand_are_absent(self) -> None:
        tracked_files = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        tracked_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8") for path in tracked_files
        ).casefold()
        retired_terms = (
            "_".join(("review", "runner")),
            " ".join(("hash", "chain")),
            " ".join(("successor", "receipt")),
            " ".join(("runner", "epoch")),
            " ".join(("bootstrap", "attestation")),
            " ".join(("retry", "challenge")),
            "-".join(("self", "hosted")) + " review",
            " ".join(("canonical", "series")),
            "-".join(("native", "codex", "loop")),
            " ".join(("native", "codex", "loop")),
        )
        for retired in retired_terms:
            self.assertNotIn(retired, tracked_text)


if __name__ == "__main__":
    unittest.main()
