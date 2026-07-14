from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/happycodex/SKILL.md"
PACKETS = ROOT / "skills/happycodex/references/task-packets.md"
EXTERNAL_REVIEW = ROOT / "skills/happycodex/references/external-review.md"
README = ROOT / "README.md"
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"


def folded(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").casefold().split())


def bundle_files() -> list[str]:
    files = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for pending in (MARKETPLACE, EXTERNAL_REVIEW):
        relative = pending.relative_to(ROOT).as_posix()
        if pending.exists() and relative not in files:
            files.append(relative)
    return files


class HappyCodexContractTests(unittest.TestCase):
    def test_plugin_is_a_small_skill_bundle_without_custom_runtime(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "happycodex")
        self.assertEqual(manifest["skills"], "./skills/")
        for surface in ("hooks", "mcpServers", "apps"):
            self.assertNotIn(surface, manifest)

        tracked_files = bundle_files()
        self.assertEqual(
            set(tracked_files),
            {
                ".codex-plugin/plugin.json",
                ".agents/plugins/marketplace.json",
                ".gitignore",
                "README.md",
                "skills/happycodex/SKILL.md",
                "skills/happycodex/agents/openai.yaml",
                "skills/happycodex/references/external-review.md",
                "skills/happycodex/references/task-packets.md",
                "tests/test_contracts.py",
            },
        )

    def test_public_marketplace_exposes_the_repo_root_plugin(self) -> None:
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "happycodex")
        self.assertEqual(marketplace["interface"]["displayName"], "HappyCodex")
        self.assertEqual(len(marketplace["plugins"]), 1)

        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "happycodex")
        self.assertEqual(
            entry["source"],
            {
                "source": "local",
                "path": "./",
            },
        )
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Productivity")

    def test_bundle_checks_ignore_unrelated_untracked_files(self) -> None:
        probe = ROOT / ".happycodex-untracked-probe"
        self.assertFalse(probe.exists())
        probe.write_text("not part of the plugin bundle\n", encoding="utf-8")
        try:
            self.assertNotIn(probe.name, bundle_files())
        finally:
            probe.unlink()

    def test_manifest_and_readme_make_installation_and_discovery_explicit(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["homepage"], "https://github.com/cch96/happycodex#readme")
        self.assertEqual(manifest["repository"], "https://github.com/cch96/happycodex")
        self.assertEqual(manifest["author"]["url"], "https://github.com/cch96")
        for keyword in (
            "long-running-tasks",
            "cross-cutting",
            "refactoring",
            "code-review",
            "testing",
            "public-contracts",
            "migrations",
            "persistence",
            "concurrency",
        ):
            self.assertIn(keyword, manifest["keywords"])

        readme = README.read_text(encoding="utf-8")
        for phrase in (
            "codex plugin marketplace add cch96/happycodex",
            "codex plugin add happycodex@happycodex",
            "Start a new Codex task",
            "## When to use it",
            "## Install",
            "$happycodex:happycodex",
        ):
            self.assertIn(phrase, readme)
        self.assertNotRegex(readme, r"\$happycodex(?!:happycodex)")

    def test_skill_uses_native_state_and_one_root_writer(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        body_folded = " ".join(body.casefold().split())

        self.assertIn("name: happycodex", frontmatter)
        self.assertIn(
            "description: Reliability workflow for long-running or high-risk",
            frontmatter,
        )
        self.assertIn("skip routine localized edits", frontmatter.casefold())
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

    def test_optional_fable_review_is_explicit_independent_and_bounded(self) -> None:
        skill = folded(SKILL)
        policy = folded(EXTERNAL_REVIEW)

        for phrase in (
            "native review remains the default",
            "explicit user instruction or applicable `agents.md` rule",
            "references/external-review.md",
            "never infer permission from risk",
        ):
            self.assertIn(phrase, skill)

        for phrase in (
            "resolve model and effort independently",
            "explicit current user instruction, applicable scoped `agents.md`",
            "`fable 5` and `max`",
            "do not silently downgrade",
            "makes fable conditional",
            "otherwise stop the task and report",
            "same frozen candidate",
            "neutral review brief",
            "run them concurrently when",
            "other reviewer's output",
            "do not vote",
            "root independently reproduces or otherwise verifies",
            "at most once",
            "sole rerun exception",
            "required for completion",
            "confirmed or unresolved material finding",
        ):
            self.assertIn(phrase, policy)
        self.assertNotIn("ask once", policy)
        self.assertNotIn("high-risk task has no recorded preference", policy)

        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertEqual(len(prompts), 3)
        self.assertTrue(all("$happycodex:happycodex" in prompt for prompt in prompts))
        self.assertTrue(all(len(prompt) <= 128 for prompt in prompts))
        self.assertNotIn("Fable", prompts[0])
        self.assertIn(
            "Use $happycodex:happycodex with Fable 5 max review when available.",
            prompts,
        )

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
        self.assertLessEqual(
            len(EXTERNAL_REVIEW.read_text(encoding="utf-8").splitlines()), 45
        )
        self.assertLessEqual(len(README.read_text(encoding="utf-8").splitlines()), 80)

        config = (ROOT / "skills/happycodex/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("$happycodex:happycodex", config)
        self.assertNotRegex(config, r"\$happycodex(?!:happycodex)")
        self.assertNotIn("dependencies:", config)

        manifest_path = ROOT / ".codex-plugin/plugin.json"
        manifest = folded(manifest_path)
        self.assertIn("acceptance evidence", manifest)
        self.assertIn("native review", manifest)
        self.assertIn("immutable task baseline", manifest)
        self.assertNotIn("immutable task scope", manifest)
        self.assertNotIn("dependency-aware read-only scouts", manifest)
        self.assertIn("$happycodex:happycodex", manifest)
        self.assertNotRegex(
            manifest_path.read_text(encoding="utf-8"),
            r"\$happycodex(?!:happycodex)",
        )

    def test_retired_protocol_and_brand_are_absent(self) -> None:
        tracked_files = bundle_files()
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
