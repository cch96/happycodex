from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/happycodex/SKILL.md"
PACKETS = ROOT / "skills/happycodex/references/task-packets.md"
EXECPLANS = ROOT / "skills/happycodex/references/execplans.md"
NATIVE_REVIEW = ROOT / "skills/happycodex/references/native-review.md"
EVALUATION = ROOT / "skills/happycodex/references/evaluation.md"
EXTERNAL_REVIEW = ROOT / "skills/happycodex/references/external-review.md"
README = ROOT / "README.md"
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"


def folded(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").casefold().split())


def tracked_files() -> list[str]:
    return subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()


def bundle_files() -> list[str]:
    files = tracked_files()
    files = [path for path in files if not path.startswith("docs/execplans/")]
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
                "skills/happycodex/references/execplans.md",
                "skills/happycodex/references/evaluation.md",
                "skills/happycodex/references/external-review.md",
                "skills/happycodex/references/native-review.md",
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

    def test_required_release_contracts_are_tracked_not_merely_present(self) -> None:
        tracked = set(tracked_files())
        for path in (
            MARKETPLACE,
            EXTERNAL_REVIEW,
            EXECPLANS,
            EVALUATION,
            NATIVE_REVIEW,
            ROOT / "skills/happycodex/agents/openai.yaml",
        ):
            self.assertIn(path.relative_to(ROOT).as_posix(), tracked)

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
            "explicit user approval",
            "immutable task baseline",
            "acceptance criteria",
            "accepted baseline failures",
            "preserved pre-existing",
            "scope changes",
        ):
            self.assertIn(phrase, body_folded)

    def test_goal_prompting_is_narrow_and_defaults_to_native_plan(self) -> None:
        skill = folded(SKILL)
        readme = folded(README)

        for phrase in (
            "unattended or automatic continuation",
            "ask once whether to enable it",
            "otherwise do not raise goal",
            "without explicit approval, continue with the native plan",
        ):
            self.assertIn(phrase, skill)

        self.assertIn("unattended or automatic continuation", readme)
        self.assertIn("without approval, it continues with the native plan", readme)

    def test_execplan_bootstraps_a_durable_completion_contract(self) -> None:
        self.assertTrue(EXECPLANS.exists())
        skill = folded(SKILL)
        contract = folded(EXECPLANS)

        for phrase in (
            "references/execplans.md",
            "before extended research",
            "repository policy",
            "docs/execplans/<task-slug>.md",
            "original outcome verbatim",
            "accepted baseline failures",
            "pending gates",
            "commit the skeleton",
        ):
            self.assertIn(phrase, f"{skill} {contract}")

        for phrase in (
            "human-readable markdown",
            "durable completion contract",
            "native plan is the current execution cursor",
            "no fixed step count",
            "git and tests are facts",
            "goal never replaces the execplan",
            "task state json",
        ):
            self.assertIn(phrase, contract)
        self.assertIn(
            "leave the retrospective empty until the task actually completes",
            contract,
        )
        self.assertNotIn("until a milestone or the task", contract)

    def test_boundary_freeze_is_independent_exhaustive_and_reproducible(self) -> None:
        text = f"{folded(SKILL)} {folded(EXECPLANS)} {folded(PACKETS)}"
        for phrase in (
            "entry points",
            "persisted routing",
            "producers and consumers",
            "background workers",
            "configuration and deployment",
            "readiness, observability, and recovery",
            "migration and rollback",
            "legacy paths",
            "exclusive or unique",
            "all or every",
            "end-to-end",
            "production-ready",
            "replacement or retirement",
            "without root's inventory",
            "reconcile the union",
            "root reproduces",
            "native agent or task id",
            "root re-read or second search does not count",
            "gate remains open",
            "cannot verify both dispatch and return",
        ):
            self.assertIn(phrase, text)

    def test_frozen_contract_cannot_be_silently_narrowed(self) -> None:
        text = folded(EXECPLANS)
        for phrase in (
            "`open`, `verified`, or `n/a`",
            "concrete path, search, command, or behavioral evidence",
            "contract-freeze commit",
            "add obligations autonomously",
            "delete, downgrade, or newly mark",
            "explicit user authorization",
            "may only add or stop",
            "affected evidence becomes stale",
        ):
            self.assertIn(phrase, text)

    def test_vertical_milestones_and_compaction_recover_from_facts(self) -> None:
        text = f"{folded(SKILL)} {folded(EXECPLANS)}"
        for phrase in (
            "independently verifiable vertical milestone",
            "semantic commit",
            "smallest meaningful red oracle",
            "focused and cumulative checks",
            "defaults, boundaries, type semantics, malformed input",
            "after resume or compaction",
            "execplan, native plan, git, tests",
            "conversation summary is not authoritative",
            "missing or inaccessible scout remains pending",
        ):
            self.assertIn(phrase, text)

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
        self.assertTrue(NATIVE_REVIEW.exists())
        skill = folded(SKILL)
        text = f"{skill} {folded(NATIVE_REVIEW)}"
        for phrase in (
            'model_reasoning_effort="max"',
            "inherit the configured review model",
            "do not hard-code a model slug",
            "never silently downgrade",
            "custom prompt conflicts with",
            "references/native-review.md",
            "complete task diff",
            "immutable task baseline",
            "contract-freeze commit",
            "verification evidence",
            "accepted baseline failures",
            "writer's implementation narrative",
            "independently reproduce",
            "at most one fresh re-review",
            "literal zero-finding result is unnecessary",
            "normalize task state before review",
            "clean task-only commit",
            "git diff <task-baseline>..head",
            "task-owned staged, unstaged, and untracked",
            "list task-owned untracked paths explicitly",
            "scope integrity",
            "truncation",
            "repository-wide completeness",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn('review_model="gpt-5.6-sol"', text)

    def test_native_review_discovers_before_contract_mapping(self) -> None:
        text = folded(NATIVE_REVIEW)
        neutral_brief = text.split("build a neutral brief", 1)[1].split(
            "## launch the dedicated reviewer", 1
        )[0]
        phase_one = text.split("## phase 1", 1)[1].split("## phase 2", 1)[0]
        phase_two = text.split("## phase 2", 1)[1].split(
            "## scope integrity", 1
        )[0]

        for phrase in (
            "do not read the execplan",
            "independent obligation inventory",
            "correctness and adversarial",
            "original outcome",
            "repository",
        ):
            self.assertIn(phrase, phase_one)

        for phrase in (
            "contract-bearing sections",
            "completeness",
            "pending gates",
            "pending scouts and worktrees",
            "review-receipt and evidence freshness",
            "decision log",
            "surprises & discoveries",
            "historical findings",
            "outcomes & retrospective",
        ):
            self.assertIn(phrase, phase_two)
        self.assertIn("current execplan path", neutral_brief)

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
        text = folded(NATIVE_REVIEW)
        clause = text.split("at most one fresh re-review", 1)[1].split(
            "## review receipt", 1
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

    def test_evaluation_covers_fail_closed_behavior_scenarios(self) -> None:
        self.assertTrue(EVALUATION.exists())
        text = folded(EVALUATION)
        for phrase in (
            "only when changing the happycodex workflow",
            "do not load this reference for ordinary user tasks",
            "boundary omission",
            "reachable legacy entry",
            "missing worker or deployment configuration",
            "frozen-contract narrowing",
            "pre-freeze compaction",
            "lost scout",
            "dirty or untracked task files",
            "accepted baseline failures",
            "review anchoring",
            "large-diff truncation",
            "expected fail-closed behavior",
            "observable evidence",
            "fresh read-only forward runs",
            "raw artifacts",
            "do not leak the expected answer",
            "execplan, git, and tests",
            "conversation summary",
            "in-flight agent handle",
        ):
            self.assertIn(phrase, text)

    def test_paired_holdout_is_blinded_adaptive_and_costed(self) -> None:
        text = folded(EVALUATION)
        for phrase in (
            "current version versus candidate",
            "same model, reasoning effort, repository snapshot, task, budget, and oracle",
            "isolated codex homes and worktrees",
            "zero implementation prompts",
            "out-of-diff system seam",
            "mechanical or behavioral oracle",
            "freeze before unsealing",
            "blind evaluator",
            "candidate's first completion-blocking regression",
            "run a second pair",
            "run a third pair",
            "candidate must be no worse",
            "false completion",
            "wall time",
            "uncached input and output tokens",
            "25 percent",
            "explicit user confirmation",
            "one pair is directional, not causal",
            "durable artifact locator",
            "exact model and reasoning effort",
            "fixture commit",
            "elapsed time",
            "missing metadata keeps the gate open",
        ):
            self.assertIn(phrase, text)

        release = text.split("## release gate", 1)[1]
        for phrase in (
            "keep the manifest, readme, and release metadata at 0.2",
            "micro suite, fresh native review, paired holdouts, and cost policy",
            "only after all of those gates pass",
            "set the public base version to `0.3.0`",
        ):
            self.assertIn(phrase, release)

    def test_release_requires_isolated_install_and_fresh_discovery(self) -> None:
        text = folded(EVALUATION)
        for phrase in (
            "isolated codex_home",
            "marketplace install",
            "fresh codex task",
            "skill discovery",
            "do not hand-edit marketplace state",
            "active installation",
        ):
            self.assertIn(phrase, text)

        manifest = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertRegex(
            manifest["version"], r"^0\.2\.0\+codex\.[A-Za-z0-9.-]+$"
        )
        self.assertIn("system-boundaries", manifest["keywords"])
        self.assertIn("execplans", manifest["keywords"])

        config = (ROOT / "skills/happycodex/agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        short = re.search(r'^  short_description: "([^"]+)"$', config, re.MULTILINE)
        self.assertIsNotNone(short)
        assert short is not None
        self.assertGreaterEqual(len(short.group(1)), 25)
        self.assertLessEqual(len(short.group(1)), 64)
        self.assertIn("$happycodex:happycodex", config)

        public = folded(README)
        for phrase in (
            "execplan stores the durable completion contract",
            "native plan stores the current execution cursor",
            "git and tests store facts",
            "independent boundary challenger",
            "two-stage fresh review",
        ):
            self.assertIn(phrase, public)
        self.assertNotIn("happycodex 0.3", public)

    def test_recovery_and_completion_reconcile_durable_evidence(self) -> None:
        text = f"{folded(SKILL)} {folded(NATIVE_REVIEW)}"
        for phrase in (
            "after resume or compaction",
            "git status",
            "git log",
            "task diff",
            "avoid repeating completed",
            "material state or ownership",
            "every acceptance criterion maps to behavior or reproducible evidence",
            "scouts and worktrees are accounted for",
            "completion-blocking",
            "original outcome",
            "safety or data integrity",
            "production operation",
            "exhaustive or retirement claim",
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
            "gate id",
            "persisted status",
            "before dispatch",
            "without root's inventory",
            "remains pending",
        ):
            self.assertIn(phrase, packet)
        self.assertNotIn("plan challenge", packet)
        self.assertNotIn("sha256", packet)

    def test_bundle_stays_concise_and_metadata_matches_the_workflow(self) -> None:
        self.assertLessEqual(len(SKILL.read_text(encoding="utf-8").splitlines()), 130)
        self.assertLessEqual(len(PACKETS.read_text(encoding="utf-8").splitlines()), 55)
        self.assertLessEqual(len(EXECPLANS.read_text(encoding="utf-8").splitlines()), 180)
        self.assertLessEqual(
            len(NATIVE_REVIEW.read_text(encoding="utf-8").splitlines()), 180
        )
        self.assertLessEqual(
            len(EXTERNAL_REVIEW.read_text(encoding="utf-8").splitlines()), 45
        )
        self.assertLessEqual(
            len(EVALUATION.read_text(encoding="utf-8").splitlines()), 200
        )
        self.assertLessEqual(len(README.read_text(encoding="utf-8").splitlines()), 100)

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
