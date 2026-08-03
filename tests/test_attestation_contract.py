from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import unittest

from evaluation.identity import evaluator_components, product_artifact_from_git
from evaluation.records import RECORD_TYPES


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "execplans" / "happycodex-evaluator-attestation.md"
PRESERVED_SKILL_TREE = "d9e525a267fbf36669d409ba1b4b009a6beeeea5"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


class RepositoryContractTests(unittest.TestCase):
    def test_product_tree_is_exact_v065_and_has_no_diff(self):
        self.assertEqual(git("rev-parse", "HEAD:skills/happycodex"), PRESERVED_SKILL_TREE)
        self.assertEqual(git("rev-parse", "v0.6.5:skills/happycodex"), PRESERVED_SKILL_TREE)
        self.assertEqual(git("diff", "--name-only", "v0.6.5", "--", "skills/happycodex"), "")

    def test_evaluator_only_commit_does_not_change_product_artifact(self):
        role = "3" * 64
        baseline = product_artifact_from_git(ROOT, "v0.6.5", external_role_config_sha256=role)
        current = product_artifact_from_git(ROOT, "HEAD", external_role_config_sha256=role)
        self.assertEqual(current, baseline)

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
        self.assertLessEqual(sum(counts.values()), 3200)
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


if __name__ == "__main__":
    unittest.main()
