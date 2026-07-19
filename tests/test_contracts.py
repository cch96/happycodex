from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "happycodex"
SKILL = SKILL_ROOT / "SKILL.md"
EXECPLAN = SKILL_ROOT / "references" / "execplan.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
README = ROOT / "README.md"

EXPECTED_RUNTIME_FILES = {
    "skills/happycodex/SKILL.md",
    "skills/happycodex/agents/openai.yaml",
    "skills/happycodex/references/execplan.md",
}
FORBIDDEN_PLUGIN_SURFACES = (
    ".app.json",
    ".mcp.json",
    "hooks.json",
    "hooks",
    "apps",
    "mcp",
    "scripts",
    "skills/happycodex/hooks",
    "skills/happycodex/scripts",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def folded(path: Path) -> str:
    return " ".join(read(path).casefold().split())


def relative_files(root: Path) -> set[str]:
    return {
        path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file()
    }


def parse_simple_yaml_mapping(text: str) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, separator, raw_value = raw_line.strip().partition(":")
        if not separator or not key:
            raise ValueError(f"unsupported YAML line: {raw_line!r}")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        value = raw_value.strip()
        if value:
            parent[key] = json.loads(value) if value.startswith('"') else value
        else:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
    return root


def runtime_markdown_budget() -> tuple[int, int]:
    lines = words = 0
    for path in (SKILL, EXECPLAN):
        text = read(path)
        lines += len(text.splitlines())
        words += len(text.split())
    return lines, words


def headings(path: Path) -> list[str]:
    return re.findall(r"^#{1,6} .+$", read(path), flags=re.MULTILINE)


class HappyCodexContractTests(unittest.TestCase):
    def test_runtime_surface_is_exact_and_has_no_custom_engine(self) -> None:
        self.assertEqual(relative_files(SKILL_ROOT), EXPECTED_RUNTIME_FILES)

        manifest = json.loads(read(MANIFEST))
        self.assertEqual(manifest["name"], "happycodex")
        self.assertEqual(manifest["skills"], "./skills/")
        for key in ("hooks", "mcpServers", "apps"):
            self.assertNotIn(key, manifest)
        for relative in FORBIDDEN_PLUGIN_SURFACES:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_untracked_runtime_probe_is_visible_to_the_oracle(self) -> None:
        probe_root = SKILL_ROOT / "hooks"
        probe = probe_root / "unexpected.py"
        self.assertFalse(probe.exists())
        probe_root.mkdir()
        probe.write_text("raise RuntimeError('must be detected')\n", encoding="utf-8")
        try:
            self.assertIn(
                "skills/happycodex/hooks/unexpected.py",
                relative_files(SKILL_ROOT),
            )
            self.assertNotEqual(relative_files(SKILL_ROOT), EXPECTED_RUNTIME_FILES)
        finally:
            probe.unlink()
            probe_root.rmdir()

    def test_hidden_runtime_probe_is_visible_to_the_oracle(self) -> None:
        probe_root = SKILL_ROOT / "__pycache__"
        probe = probe_root / "hidden.cpython-313.pyc"
        self.assertFalse(probe.exists())
        probe_root.mkdir()
        probe.write_bytes(b"unexpected packaged bytecode")
        try:
            self.assertIn(
                "skills/happycodex/__pycache__/hidden.cpython-313.pyc",
                relative_files(SKILL_ROOT),
            )
            self.assertNotEqual(relative_files(SKILL_ROOT), EXPECTED_RUNTIME_FILES)
        finally:
            probe.unlink()
            probe_root.rmdir()

    def test_python_validation_uses_only_declared_stdlib_dependencies(self) -> None:
        allowed = set(sys.stdlib_module_names) | {"__future__", "evaluation"}
        for path in (
            *sorted((ROOT / "evaluation").rglob("*.py")),
            *ROOT.glob("tests/*.py"),
        ):
            imported: set[str] = set()
            for node in ast.walk(ast.parse(read(path), filename=str(path))):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".", 1)[0])
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(imported - allowed, set())

    def test_runtime_markdown_meets_clean_room_budget(self) -> None:
        lines, words = runtime_markdown_budget()
        self.assertLessEqual(lines, 262)
        self.assertLessEqual(words, 2_400)

    def test_skill_frontmatter_and_reference_graph_are_closed(self) -> None:
        text = read(SKILL)
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)
        parsed = parse_simple_yaml_mapping(frontmatter)
        self.assertEqual(set(parsed), {"name", "description"})
        self.assertEqual(parsed["name"], "happycodex")
        self.assertIn("high-risk", parsed["description"].casefold())
        self.assertIn("skip", parsed["description"].casefold())

        links = re.findall(r"`(references/[^`]+\.md)`", body)
        self.assertEqual(links, ["references/execplan.md"])
        self.assertTrue(EXECPLAN.is_file())
        runtime = "\n".join(read(path) for path in (SKILL, EXECPLAN))
        self.assertNotIn("references/task-packets.md", runtime)
        self.assertNotIn("references/external-review.md", runtime)

    def test_execplan_template_has_one_typed_ledger_and_checkpoint(self) -> None:
        self.assertEqual(
            headings(EXECPLAN),
            [
                "# HappyCodex 0.3 ExecPlan",
                "## When to create it",
                "## Template",
                "### Outcome and baseline",
                "### Claims Ledger",
                "### Checkpoint",
                "### Retrospective",
                "## Neutral review brief",
                "## Coverage receipt",
            ],
        )
        text = read(EXECPLAN)
        self.assertEqual(text.count("### Claims Ledger"), 1)
        self.assertIn(
            "| ID | Type | Claim | Closure | Falsifier / oracle | Evidence | State |",
            text,
        )
        for claim_type in ("outcome", "preservation", "allowed-break", "premise"):
            self.assertIn(f"`{claim_type}`", text)
        self.assertIn("only `open`, `verified`, or `N/A`", text)
        self.assertIn("`N/A` requires", text)
        self.assertIn("every claim is verified or evidence-backed `N/A`", read(SKILL))
        for phrase in (
            "repository policy",
            "authorization anchor/hash",
            "affected claims",
            "invalidated evidence",
            "required reruns",
        ):
            self.assertIn(phrase, folded(SKILL) + " " + folded(EXECPLAN))

    def test_native_state_roles_and_goal_are_nonoverlapping(self) -> None:
        text = folded(SKILL)
        self.assertIn("root is the only writer", text)
        self.assertIn("native plan is only the current cursor", text)
        self.assertIn("goal is only an objective pointer", text)
        for phrase in (
            "authorization permits actions",
            "execplan defines completion",
            "evidence binds a candidate",
            "goal controls automatic continuation",
            "never infer one from another",
        ):
            self.assertIn(phrase, text)
        self.assertIn("requiring explicit approval", text)
        self.assertIn(
            "ask once only if unattended continuation lacks a goal choice", text
        )
        self.assertIn("declining keeps native plan active", text)
        self.assertIn("native goal", text)
        self.assertIn("goal and outcome diverge", text)
        self.assertNotIn("neither requests nor changes", text)
        self.assertIn("no fixed step cap", text)
        self.assertIn(
            "restore the execplan before any write, review, or completion", text
        )
        self.assertIn("mark the matching goal complete", text)
        self.assertIn("only after every completion gate", text)
        for phrase in (
            "no safe in-scope progress remains",
            "persistent user-decision, destructive-action, external-dependency, or cost/complexity wait",
            "natively pause active goal",
            "goal-stop guard",
            "`/goal pause` is a mandatory open gate",
            "tell the user to run `/goal pause`",
            "turn end, interrupt, transient platform error, review finding",
            "blocked is not pause",
            "goal wake or resume continues existing authority",
            "never authorizes an amendment, waiver, review, or cost increase",
            "stop waiting cancels only the current wait",
            "does not waive a gate",
            "goal clear abandons",
            "read final visible goal state",
        ):
            self.assertIn(phrase, text)

    def test_qualification_has_safe_upgrade_and_low_risk_exit(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "clearly local, low-risk task",
            "uncertainty qualifies",
            "before extended research",
            "becomes qualifying after edits",
            "public-contract or behavior-changing after edits",
            "establish the execplan before the next product write",
            "true pre-task baseline",
            "without that selection, stop",
            "commit this minimal skeleton immediately",
            "before investigation or challenger dispatch",
            "freeze later in a separate revision",
            "distinct contract-freeze revision",
            "production-cutover",
            "stop and ask the user",
        ):
            self.assertIn(phrase, text)

    def test_design_exploration_stops_at_requirement_saturation(self) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for phrase in (
            "materially distinct",
            "decision-changing",
            "challenge omissions",
            "no clearly better",
            "requirements-based saturation",
            "cosmetic",
        ):
            self.assertIn(phrase, text)

    def test_boundary_freeze_preserves_independence_and_compatibility(self) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for phrase in (
            "entrypoints",
            "persisted routing",
            "producers/consumers",
            "configuration/deployment",
            "observability/recovery",
            "migration/rollback",
            "reachable legacy bypasses",
            "authoring/input",
            "validation",
            "persistence/serialization",
            "user-visible output",
            "defaults, boundaries, type semantics, malformed input",
            "no inherited root conversation",
            "not root's inventory",
            "every scout, challenger, and reviewer is read-only",
            "one bounded question",
            "named decision",
            "do not target",
            "parallelize only independent",
            "never delegates",
            "duplicate question",
            "architecture-shaping",
            "all/only/end-to-end/production-ready/replacement/retirement",
            "unique",
            "fresh baseline-only challenger",
            "revision/tree and dirty state",
            "stop condition",
            "remaining uncertainty",
            "root reproduces",
            "writer summary that an agent completed is not a receipt",
            "reachable matching terminal record",
            "writer completion sentence cannot substitute",
        ):
            self.assertIn(phrase, text)
        ordinary_scout = (
            folded(SKILL)
            .split("a scout gets", 1)[1]
            .split("every scout, challenger, and reviewer", 1)[0]
        )
        for phrase in (
            'fork_turns="none"',
            "no inherited root conversation",
            "neutral packet",
            "no preferred answer",
        ):
            self.assertIn(phrase, ordinary_scout)
        self.assertLess(
            folded(SKILL).index('fork_turns="none"'),
            folded(SKILL).index("for exhaustive or architecture-shaping"),
        )
        self.assertNotIn("administrative closure commit", text)
        self.assertNotIn("make the separate contract-freeze commit", text)

    def test_contract_is_frozen_while_entailed_inventory_can_grow(
        self,
    ) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for source in (folded(SKILL), folded(EXECPLAN)):
            self.assertIn("revision freezes the user contract", source)
        self.assertNotIn("before symmetric freeze", text)
        for phrase in (
            "operative sources",
            "normalized outcome",
            "exclusions",
            "allowed breaks",
            "monotonically add",
            "derived claim",
            "entailed by",
            "provenance",
            "external backlog",
            "removing or narrowing",
            "widening",
            "explicit user authorization",
            "dependent evidence",
            "advance a baseline",
            "verbatim authorization",
            "reopen",
            "positive claim",
            "using `n/a`",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("adding, removing or narrowing claims", text)

    def test_recovery_and_no_commit_modes_are_fact_based(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "semantic commit trailer",
            "unique task-owned 0.3 execplan",
            "reachable private git ref",
            "approved content-addressed archive",
            "user-selected durable location",
            "without that selection, stop",
            "skeleton, freeze, every green slice, and closure",
            "administrative closure revision",
            "missing agent",
            "before writing",
            "facts win",
            "native compaction",
            "resume of the same task",
            "post-resume",
            "conversation summary",
            "live handle",
            "prose claim",
            "do not run a full reviewer after every revision",
            "tests and compatibility counterexamples to affected obligations/gates",
            "baseline, writer ownership, current milestone, pending gates, test status, and worktree",
            "ask the user for the missing material fact",
            "maintainer evaluation",
            "not each user task",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("also run a fresh no-summary/no-handle control", text)

    def test_review_identity_is_product_tree_not_control_record_head(self) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for phrase in (
            "two neutral commits",
            "exclude only the sole execplan",
            "product-tree identity",
            "diff-unit inventory",
            "source baseline",
            "source baseline/candidate",
            "manifest equality",
            "staged, unstaged, and untracked",
            "clean review snapshot",
            "phase 1",
            "dedicated native `codex review`",
            "inherits the configured model",
            "if unset, prefer `gpt-5.6-sol`",
            "strongest user/environment-authorized read-only",
            "`ultra` requires explicit authorization",
            "selector flags separate from the stdin brief",
            "contract-only projection",
            "same fresh reviewer session",
            "map its independent inventory",
            "stable numbered obligation ids and text",
            "correctness/adversarial",
            "every independent obligation and diff unit",
            "only then reveal",
            "do not reveal the contract",
            "receipt-only correction",
            "writer narrative",
            "coverage receipt",
            "detailed findings stay in the native review output",
            "administrative closure revision",
            "product tree is unchanged",
            "any product change invalidates",
            "material evidence-only change invalidates affected review evidence",
            "minimally invalidated behavior/review/holdout receipts",
            "expected rerun cost",
            "required user decision",
        ):
            self.assertIn(phrase, text)

    def test_review_handles_contamination_truncation_and_external_review(self) -> None:
        text = folded(SKILL)
        for phrase in (
            "original git metadata",
            "root conversation",
            "declared dependency",
            "missing diff unit",
            "truncation",
            "independent obligation",
            "no fixed review-count quota",
            "never rerun an unchanged candidate",
            "explicitly requested external reviewer",
            "same synthetic scope",
            "union findings without voting",
            "fable 5",
            "defaults to `max`",
            "never downgrade, substitute, install, enable, or search",
            "detached desktop",
            "fresh detached",
            "original request or frozen acceptance",
            "safety or data integrity",
            "production condition",
            "exhaustive replacement or retirement",
            "behavior proven by the last accepted receipt",
            "disputed classification or repeated repaired-case failure stops for the user",
            "configured-model source",
            "effective permission profile",
            "rejected counter-evidence",
            "external backlog",
            "risk-bearing milestone",
            "full final-candidate review",
            "durable output destination",
            "foreground buffer is not a receipt",
            "resolve its durable terminal record before rerun",
            "runtime-issued command/session/effective-model receipt",
            "agent or task name never proves reviewer identity",
            "task-scoped",
            "advisory-once",
            "exact-final gate",
            "unavailable: a required review stops",
            "`when available` continues with one disclosed skip",
        ):
            self.assertIn(phrase, text)

    def test_wait_waiver_and_new_phase_boundaries_are_explicit(self) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for phrase in (
            "only explicit user text waives a named gate",
            "exact waiver scope",
            "outside that scope reopens the gate",
            "disclose every unrun gate",
            "new independent outcome or baseline",
            "new task and execplan",
            "in-contract repair stays",
        ):
            self.assertIn(phrase, text)

    def test_current_contract_has_no_stale_review_inventory_counts(self) -> None:
        current = (
            read(SKILL)
            + read(EXECPLAN)
            + "".join(
                read(path) for path in sorted((ROOT / "evaluation").rglob("*.py"))
            )
            + "".join(
                read(path)
                for path in sorted((ROOT / "evaluation/cases").glob("*.json"))
            )
        )
        self.assertNotRegex(current, r"\b(?:106|33)\b")

    def test_retrospective_is_final_only(self) -> None:
        text = folded(EXECPLAN)
        self.assertIn("fill only after final completion", text)
        self.assertIn("do not expose it to a reviewer", text)

    def test_secret_and_baseline_failure_rules_are_differential(self) -> None:
        text = folded(SKILL) + " " + folded(EXECPLAN)
        for phrase in (
            "never persist a secret",
            "structured failure identities",
            "new product-tree secret finding",
            "pre-existing finding",
            "enumerate material findings—including goal/outcome divergence—by stable identity",
            "baseline-unchanged, resolved, candidate-new, or unknown",
            "classify current blockers",
            "unknown remains open",
            "classify by finding id, not surrounding text",
            "never omit a baseline finding",
            "cannot be relabeled as baseline",
            "explicitly accepted and unchanged",
            "unaccepted baseline failure",
        ):
            self.assertIn(phrase, text)

    def test_public_install_and_invocation_surfaces_remain_coherent(self) -> None:
        marketplace = json.loads(read(MARKETPLACE))
        self.assertEqual(marketplace["interface"]["displayName"], "HappyCodex")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(marketplace["name"], "happycodex")
        self.assertEqual(entry["name"], "happycodex")
        self.assertEqual(entry["source"], {"source": "local", "path": "./"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Productivity")

        manifest = json.loads(read(MANIFEST))
        self.assertEqual(
            manifest["homepage"], "https://github.com/cch96/happycodex#readme"
        )
        self.assertEqual(manifest["repository"], "https://github.com/cch96/happycodex")
        self.assertEqual(manifest["author"]["url"], "https://github.com/cch96")
        for keyword in (
            "codex",
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

        public = read(README)
        for phrase in (
            "codex plugin marketplace add cch96/happycodex",
            "codex plugin add happycodex@happycodex",
            "Start a new Codex task",
            "$happycodex:happycodex",
            "Fable 5 max",
        ):
            self.assertIn(phrase, public)
        self.assertIn("asks once", public)
        self.assertIn(
            "declining keeps native plan active", " ".join(public.casefold().split())
        )
        self.assertNotIn("never asks you to enable Goal", public)
        self.assertIn("only when you explicitly request it", public)

    def test_ui_metadata_is_namespaced_and_small(self) -> None:
        config = parse_simple_yaml_mapping(read(OPENAI_YAML))
        self.assertEqual(set(config), {"interface"})
        interface = config["interface"]
        self.assertEqual(
            set(interface), {"display_name", "short_description", "default_prompt"}
        )
        self.assertEqual(interface["display_name"], "HappyCodex")
        self.assertGreaterEqual(len(interface["short_description"]), 25)
        self.assertLessEqual(len(interface["short_description"]), 64)
        self.assertIn("$happycodex:happycodex", interface["default_prompt"])

        manifest = json.loads(read(MANIFEST))
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in prompts))
        self.assertTrue(all("$happycodex:happycodex" in prompt for prompt in prompts))

    def test_public_surfaces_reject_bare_invocation_and_retired_branding(self) -> None:
        paths = (README, MANIFEST, MARKETPLACE, SKILL, EXECPLAN, OPENAI_YAML)
        for path in paths:
            self.assertNotRegex(read(path), r"\$happycodex(?!:happycodex)", path.name)

        public_text = "\n".join(read(path) for path in paths).casefold()
        retired_terms = (
            "review runner",
            "hash chain",
            "successor receipt",
            "runner epoch",
            "bootstrap attestation",
            "retry challenge",
            "self-hosted review",
            "canonical series",
            "native-codex-loop",
            "native codex loop",
        )
        for retired in retired_terms:
            self.assertNotIn(retired, public_text)

    def test_repository_has_no_tracked_generated_python_artifacts(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertFalse(
            any("__pycache__" in path or path.endswith(".pyc") for path in tracked)
        )


if __name__ == "__main__":
    unittest.main()
