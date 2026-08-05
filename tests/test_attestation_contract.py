from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import unittest

from evaluation.identity import evaluator_components
from evaluation.records import RECORD_TYPES
from tests.attestation_fixtures import CANDIDATE_REVISION, bundle


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "execplans" / "happycodex-evaluator-attestation.md"
ROUTING_PLAN = ROOT / "docs" / "execplans" / "happycodex-0-7-0-role-routing.md"
PRESERVED_SKILL_TREE = "d9e525a267fbf36669d409ba1b4b009a6beeeea5"
CANDIDATE_VERSION = "0.7.0"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


class RepositoryContractTests(unittest.TestCase):
    def test_published_v065_tree_is_immutable_and_candidate_is_v070(self):
        self.assertEqual(CANDIDATE_REVISION, "HEAD")
        self.assertEqual(git("rev-parse", "v0.6.5:skills/happycodex"), PRESERVED_SKILL_TREE)
        released = json.loads(git("show", "v0.6.5:.codex-plugin/plugin.json"))
        candidate = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(released["version"], "0.6.5")
        self.assertEqual(candidate["version"], CANDIDATE_VERSION)
        self.assertNotEqual(
            git("show", "v0.6.5:skills/happycodex/SKILL.md"),
            (ROOT / "skills" / "happycodex" / "SKILL.md").read_text().strip(),
        )

    def test_v070_skill_uses_material_supported_flow_boundary(self):
        raw = (ROOT / "skills" / "happycodex" / "SKILL.md").read_text()
        text = " ".join(raw.split())
        required = (
            "material failures reachable through supported workflows",
            "including compaction, concurrency, and partial effects",
            "non-adversarial but fallible",
            "verify state and identity, not motive",
            "Prefer the smallest sufficient control",
            "expanding scope or trust boundaries requires explicit user authority",
            "remaining alternatives would not change that Outcome",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        retired_vocabulary = (
            "uncertainty qualifies",
            "spoofed",
            "removes the bypass",
            "contamination",
            "never substitute a writer",
            "preferred answers",
            "evidence ledger",
            "owner token",
            "separate exact gate plan",
            "content-addressed bundle",
        )
        for retired in retired_vocabulary:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text.lower())

        authority = " ".join(raw.split("- Authority:", 1)[1].split("- Resource claims:", 1)[0].split())
        self.assertIn("exact current grant", authority)
        self.assertIn("out-of-scope authority", authority)
        self.assertNotIn("user authority permits writes", authority.lower())

        effects = " ".join(raw.split("- Cost and effects:", 1)[1].split("## Review and complete", 1)[0].split())
        for boundary in ("outcome receipt", "same authorization", "ambiguous or partial effects stop", "separate authority"):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, effects)
        for evaluator_term in ("provider", "pre-provider", "infrastructure"):
            with self.subTest(evaluator_term=evaluator_term):
                self.assertNotIn(evaluator_term, effects.lower())

    def test_v070_role_routing_contract_is_complete_and_fail_closed(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        skill = (ROOT / "skills" / "happycodex" / "SKILL.md").read_text()
        reference = (ROOT / "skills" / "happycodex" / "references" / "execplan.md").read_text()
        readme_zh = (ROOT / "README.md").read_text()
        readme_en = (ROOT / "README.en.md").read_text()
        routing_plan = ROUTING_PLAN.read_text()
        compact = " ".join(skill.split())
        ref_compact = " ".join(reference.split())
        zh_compact = " ".join(readme_zh.split())
        en_compact = " ".join(readme_en.split())
        plan_compact = " ".join(routing_plan.split())

        self.assertEqual(manifest["version"], "0.7.0")
        self.assertNotIn("agents", manifest)
        self.assertIn("host-capability-gated role routing", manifest["description"])
        self.assertIn("when the host supports exact selectors and runtime metadata", manifest["interface"]["longDescription"])

        skill_matrix = (
            "| Root | `gpt-5.6-sol` | `max` |",
            "| Explorer | `gpt-5.6-terra` | `high` |",
            "| Challenger | `gpt-5.6-sol` | `high` |",
            "| Executor | `gpt-5.6-sol` | `high` |",
            "| Exact-final | `gpt-5.6-sol` | `max` |",
        )
        for row in skill_matrix:
            with self.subTest(row=row):
                self.assertIn(row, skill)

        required_runtime = (
            "Before dispatch, Root verifies its own effective route is `gpt-5.6-sol/max`",
            "authenticated dispatch/tool receipt binding logical role",
            "requested model/effort or custom config SHA-256",
            "input baseline/candidate identities",
            "prompt/brief digest",
            "Platform acceptance of the spawn completes that dispatch receipt",
            "On the portable builtin/default path, explicitly pin model and effort",
            "its file's model and effort take precedence",
            "omit redundant or conflicting explicit model/effort arguments",
            "Dispatch may start the child immediately",
            "Runtime metadata need not repeat Root-owned logical role, fork, input identities, or prompt digest",
            "cross-binding that metadata to the authenticated dispatch receipt",
            "If either required evidence source is missing or the cross-bind mismatches",
            "must not enter the behavior plan, trigger a write grant, advance phase, or count as a final verdict",
            "interrupt the child if still running, discard its output, and fail closed",
            "Run multiple Explorers concurrently only when multiple such axes exist",
            "give each Explorer exactly one bounded question",
            "Root reproduces and merges the evidence; it never votes",
            "Challenger runs before the behavior-plan freeze",
            "Only after that freeze does the unique Executor write",
            "After candidate freeze, spawn exactly one fresh Exact-final",
            "empty history",
            "neutral brief",
            "A repair returns to `working`",
        )
        for phrase in required_runtime:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, compact)
        self.assertNotIn("runtime-issued logical role", compact)

        order = (
            "Root first decomposes the problem",
            "Challenger runs before the behavior-plan freeze",
            "Only after that freeze does the unique Executor write",
            "After candidate freeze, spawn exactly one fresh Exact-final",
        )
        positions = [compact.index(phrase) for phrase in order]
        self.assertEqual(positions, sorted(positions))

        readme_matrices = (
            (readme_en, (
                "| Root | `gpt-5.6-sol` | `max` |",
                "| Explorer | `gpt-5.6-terra` | `high` |",
                "| Challenger | `gpt-5.6-sol` | `high` |",
                "| Unique Executor | `gpt-5.6-sol` | `high` |",
                "| Unique fresh Exact-final | `gpt-5.6-sol` | `max` |",
            )),
            (readme_zh, (
                "| Root | `gpt-5.6-sol` | `max` |",
                "| Explorer | `gpt-5.6-terra` | `high` |",
                "| Challenger | `gpt-5.6-sol` | `high` |",
                "| 唯一 Executor | `gpt-5.6-sol` | `high` |",
                "| 唯一全新 Exact-final | `gpt-5.6-sol` | `max` |",
            )),
        )
        for text, rows in readme_matrices:
            for row in rows:
                with self.subTest(readme_row=row):
                    self.assertIn(row, text)

        for phrase in (
            "Complete routing applies only when the host supports exact selectors and runtime-issued metadata",
            "Before dispatch, Root verifies itself as `gpt-5.6-sol/max`",
            "Root's authenticated dispatch/tool receipt binds logical role",
            "platform acceptance of the spawn completes the dispatch receipt",
            "Runtime-issued session/turn metadata supplies",
            "it need not echo Root-owned logical role, fork, input identities, or prompt digest",
            "Root admits output only after cross-binding the dispatch receipt and runtime metadata",
            "Multiple Explorers run concurrently only when multiple such axes exist",
            "Root reproduces and merges the evidence; it never votes",
            "only after that freeze does the unique Executor write",
            "start exactly one fresh Exact-final with empty history and a neutral brief",
        ):
            self.assertIn(phrase, en_compact)
        for phrase in (
            "完整路由只在 host 支持精确 selector 和 runtime-issued metadata 时成立",
            "dispatch 前，Root 先核验自身为 `gpt-5.6-sol/max`",
            "Root 的经认证 dispatch/tool receipt 绑定逻辑角色",
            "平台接受 spawn 即完成 dispatch receipt",
            "不要求它重复 Root 已绑定的逻辑 角色、fork、输入身份或 prompt digest",
            "Root 只有交叉绑定 dispatch receipt 与 runtime metadata 后才可 admission",
            "只有存在多个这种轴时，才可并行多个",
            "Root 复现并合并证据，不投票",
            "计划冻结后才由唯一 Executor 写入",
            "后只启动一个空历史、使用中性 brief 的全新 Exact-final",
        ):
            self.assertIn(phrase, zh_compact)

        fields = (
            "Logical role", "Selected agent request", "Single question",
            "Requested route or config", "Fork mode", "Parallel independence",
            "Input identities", "Prompt/brief digest", "Spawn acceptance",
            "Actual agent role/name", "Effective route", "Effective permissions",
            "Runtime identity", "Phase", "Admission state", "Phase gate",
            "Terminal receipt",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(f"| {field} |", reference)
        dispatch_rows = (
            "Logical role", "Selected agent request", "Single question",
            "Requested route or config", "Fork mode", "Parallel independence",
            "Input identities", "Prompt/brief digest",
        )
        for field in dispatch_rows:
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("authenticated Root-owned dispatch/tool receipt", row)
        runtime_rows = (
            "Actual agent role/name", "Effective route", "Effective permissions",
            "Runtime identity",
        )
        for field in runtime_rows:
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("runtime-issued session/turn metadata", row)
        for field in ("Phase", "Admission state", "Phase gate", "Terminal receipt"):
            row = next(line for line in reference.splitlines() if line.startswith(f"| {field} |"))
            self.assertIn("Root admission record", row)
        for phrase in (
            "all child output is inadmissible",
            "Runtime metadata is not required to echo logical role, fork, input identities, or prompt digest",
            "cannot enter the behavior plan, trigger a write grant, advance phase, or count as a final verdict",
            "interrupt the child if still running, discard the output, and fail closed",
            'sandbox_mode = "read-only"',
            "read-only top-level or parent environment before dispatch",
            "unverified output remains inadmissible",
        ):
            self.assertIn(phrase, ref_compact)
        ref_order = (
            "Before dispatch, Root verifies",
            "Platform acceptance completes the authenticated dispatch receipt",
            "Root then reads the runtime-issued session/turn metadata",
            "Until both required sources cross-bind",
            "A missing source or mismatch requires Root",
            "Root decomposes the problem",
        )
        ref_positions = [ref_compact.index(phrase) for phrase in ref_order]
        self.assertEqual(ref_positions, sorted(ref_positions))

        for row in skill_matrix:
            self.assertIn(row, routing_plan)
        self.assertIn("| Challenger | `gpt-5.6-sol` | `high` | read-only, before behavior-plan freeze |", routing_plan)
        self.assertNotIn("| Challenger | `gpt-5.6-sol` | `high` | read-only, before candidate freeze |", routing_plan)
        for phrase in (
            "## Runtime routing receipts",
            "019fd0fe-6294-7270-a204-4a68d63df579",
            "019fd0fe-81ee-79c2-896d-b2c0f87203c0",
            "unknown agent_type 'happycodex_explorer'",
            "tomli 2.4.1",
            "baseline-unchanged accepted validation limitation",
            "authenticated Root-owned dispatch/tool receipt",
            "runtime-issued session/turn metadata",
            "Root admits output only after cross-binding",
            "new-task activation deferred, not a 0.7.0 source-candidate blocker",
        ):
            self.assertIn(phrase, plan_compact)

        for normalized in (compact, ref_compact, en_compact):
            self.assertIn('sandbox_mode = "read-only"', normalized)
            self.assertIn("full-access parent", normalized)
            self.assertIn("read-only top-level or parent", normalized)
        self.assertIn('sandbox_mode = "read-only"', zh_compact)
        self.assertIn("full-access 父任务", zh_compact)
        self.assertIn("read-only 顶层或父环境", zh_compact)
        self.assertIn("插件安装不打包、安装、激活或要求自定义代理", zh_compact)
        self.assertIn("Plugin installation does not bundle, install, activate, or require custom agents", en_compact)
        self.assertIn("不代表已经发布或激活", readme_zh)
        self.assertIn("does not claim that 0.7.0 has been released or activated", en_compact)

    def test_no_active_ledger_or_retired_engine_files_exist(self):
        retired = [
            "evaluation/results/current.json", "evaluation/contracts-v7.json",
            "evaluation/live.py", "evaluation/core/ledger.py",
            "evaluation/core/receipt.py", "evaluation/semantic/replay.py",
            "evaluation/corpus/engine.py", "evaluation/holdout/engine.py",
        ]
        self.assertEqual([path for path in retired if (ROOT / path).exists()], [])

    def test_only_four_durable_record_type_literals_exist(self):
        discovered = set()
        for path in (ROOT / "evaluation").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and node.value in RECORD_TYPES:
                    discovered.add(node.value)
        self.assertEqual(discovered, set(RECORD_TYPES))

    def test_no_retired_control_plane_vocabulary_in_evaluator(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "evaluation").rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
        for retired in ("GatePlan", "GateReceipt", "EvidenceJoin", "current.json", "promotion", "reconcile", "adaptive", "public-0.2"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, text)

    def test_fixed_host_raw_capture_has_no_legacy_verification_surface(self):
        roots = (ROOT / "evaluation", ROOT / "tests")
        sources = [
            path
            for root in roots
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ]
        forbidden = ("pro" + "of", "ver" + "ifier")
        offenders = [
            str(path.relative_to(ROOT))
            for path in sources
            if any(token in path.name.lower() or token in path.read_text(encoding="utf-8", errors="ignore").lower() for token in forbidden)
        ]
        self.assertEqual(offenders, [])

    def test_evaluation_python_loc_is_bounded(self):
        modules = list((ROOT / "evaluation").rglob("*.py"))
        counts = {path: len(path.read_text(encoding="utf-8").splitlines()) for path in modules}
        self.assertLess(sum(counts.values()), 3600)
        self.assertTrue(all(count <= 600 for count in counts.values()), counts)

    def test_execplan_is_bounded_current_index(self):
        text = PLAN.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 3000)
        self.assertEqual(text.count("## Current checkpoint"), 1)
        self.assertNotIn("adaptive", text.lower())
        self.assertNotIn("public-0.2", text.lower())

    def test_evaluator_components_are_separate_and_nonempty(self):
        components = evaluator_components(ROOT)
        self.assertEqual(
            set(components),
            {"evaluator_bundle_sha256", "provider_component_sha256", "oracle_component_sha256", "harness_component_sha256"},
        )
        self.assertEqual(len(set(components.values())), 4)

    def test_effect_cap_is_separate_from_ex_post_token_qualification(self):
        spec = bundle()[2]

        self.assertIn("effect_cap", spec)
        self.assertEqual(
            set(spec["effect_cap"]),
            {"model_calls", "wall_milliseconds"},
        )
        self.assertIn("token_qualification", spec)
        self.assertEqual(
            set(spec["token_qualification"]),
            {"input_tokens", "output_tokens"},
        )
        self.assertNotIn("total_cap", spec)

    def test_production_inventory_excludes_conditional_mechanisms(self):
        evaluation = ROOT / "evaluation"
        manifest = json.loads((evaluation / "manifest-v1.json").read_text())
        fixtures = json.loads((evaluation / "provider-fixtures-v1.json").read_text())
        oracles = json.loads((evaluation / "hidden-oracles-v1.json").read_text())
        schemas = json.loads((evaluation / "report-schemas-v1.json").read_text())
        expected = {
            "goal-divergence", "no-commit-secret", "qualification-high-risk",
            "qualification-low-risk", "qualification-midflight",
        }
        self.assertEqual(set(manifest["core_roles"]), expected)
        self.assertEqual(set(fixtures["core"]), expected)
        self.assertEqual(set(oracles["core"]), expected)
        self.assertEqual(set(schemas["core"]), expected)
        for retired in ("same-task-compaction", "no-summary-reconstruction"):
            self.assertNotIn(retired, str((manifest, fixtures, oracles, schemas)))

    def test_qualification_fixtures_define_one_activation_boundary_without_execution(self):
        fixtures = json.loads((ROOT / "evaluation" / "provider-fixtures-v1.json").read_text())["core"]
        expected_boundaries = {
            "qualification-high-risk": "pre-selection",
            "qualification-low-risk": "pre-selection",
            "qualification-midflight": "after-new-fact",
        }
        for role_id, boundary in expected_boundaries.items():
            case = fixtures[role_id]
            self.assertEqual(case["fixture"]["qualification_boundary"], boundary)
            self.assertIn("qualifies to activate or apply HappyCodex", case["prompt"])

        low = fixtures["qualification-low-risk"]
        self.assertEqual(
            {key: low["fixture"][key] for key in ("confirmed", "bounded", "read_only", "local")},
            {"confirmed": True, "bounded": True, "read_only": True, "local": True},
        )
        self.assertFalse(low["workspace"]["execution_required"])
        self.assertFalse(low["workspace"]["repository_write_requested"])
        self.assertFalse(low["workspace"]["external_effect_requested"])
        self.assertNotIn("empty workspace", json.dumps(low).lower())

    def test_holdout_decision_safe_semantics_are_provider_visible_and_oracle_blind(self):
        evaluation = ROOT / "evaluation"
        fixtures = json.loads((evaluation / "provider-fixtures-v1.json").read_text())["holdouts"]
        oracles = json.loads((evaluation / "hidden-oracles-v1.json").read_text())["holdouts"]
        prompts = {case["prompt"] for case in fixtures.values()}
        self.assertEqual(len(prompts), 1)
        prompt = next(iter(prompts))
        self.assertIn("recommended handling", prompt)
        self.assertIn("not whether the current scenario itself is safe", prompt)
        for case in fixtures.values():
            self.assertEqual(
                case["fixture"]["decision_safe_semantics"],
                "recommended-handling-safe-not-current-scenario-safe",
            )
        _, _, spec, _ = bundle()
        for unit in (item for item in spec["units"] if item["stage"] == "holdout"):
            projection = unit["invocation"]["provider_input"]
            self.assertEqual(
                projection["fixture"]["decision_safe_semantics"],
                "recommended-handling-safe-not-current-scenario-safe",
            )
            self.assertFalse({"oracle", "expected", "mapping"} & set(projection))
        provider_projection = json.dumps(fixtures, sort_keys=True)
        self.assertIn("decision_safe_semantics", provider_projection)
        for oracle in oracles.values():
            self.assertNotIn(json.dumps(oracle, sort_keys=True), provider_projection)


if __name__ == "__main__":
    unittest.main()
