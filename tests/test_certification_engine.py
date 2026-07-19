from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from evaluation.core.identity import (
    IdentityError,
    engine_inventory,
    package_identities,
)
from evaluation.core.impact import build_snapshot, plan_impact
from evaluation.core.receipt import load_ledger, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MODULES = {
    "evaluation/__init__.py",
    "evaluation/cli.py",
    "evaluation/core/__init__.py",
    "evaluation/core/identity.py",
    "evaluation/core/impact.py",
    "evaluation/core/receipt.py",
    "evaluation/corpus/__init__.py",
    "evaluation/corpus/contract.py",
    "evaluation/corpus/engine.py",
    "evaluation/holdout/__init__.py",
    "evaluation/holdout/blind.py",
    "evaluation/holdout/compare.py",
    "evaluation/holdout/engine.py",
}


class CertificationIdentityTests(unittest.TestCase):
    def test_inventory_classifies_every_engine_module_and_schema(self) -> None:
        first = engine_inventory(ROOT)
        second = engine_inventory(ROOT)

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], 1)
        self.assertEqual(set(first["categories"]), {"semantic", "harness", "artifact"})
        entries = {item["path"]: item["category"] for item in first["entries"]}
        self.assertEqual(
            {path for path in entries if path.endswith(".py")}, EXPECTED_MODULES
        )
        self.assertEqual(
            {item["sha256"] for item in first["entries"]},
            {item["sha256"] for item in second["entries"]},
        )
        self.assertTrue(all(first["categories"][name] for name in first["categories"]))

    def test_inventory_fails_closed_on_an_unclassified_module(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            unexpected = clone / "evaluation" / "corpus" / "unexpected.py"
            unexpected.write_text("VALUE = 1\n", encoding="utf-8")

            with self.assertRaisesRegex(IdentityError, "unclassified engine input"):
                engine_inventory(clone)

    def test_inventory_fails_closed_on_an_unclassified_schema(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            unexpected = clone / "evaluation" / "corpus" / "unexpected.json"
            unexpected.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(IdentityError, "unclassified engine input"):
                engine_inventory(clone)

    def test_release_metadata_is_artifact_only_but_skill_is_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            plugin = Path(raw) / "plugin"
            for relative in (".agents", ".codex-plugin", "README.md", "skills"):
                source = ROOT / relative
                target = plugin / relative
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)

            baseline = package_identities(plugin)
            manifest_path = plugin / ".codex-plugin" / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "0.4.0+test"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            metadata_only = package_identities(plugin)
            self.assertEqual(
                baseline["semantic_sha256"], metadata_only["semantic_sha256"]
            )
            self.assertNotEqual(
                baseline["artifact_sha256"], metadata_only["artifact_sha256"]
            )

            skill = plugin / "skills" / "happycodex" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            runtime_change = package_identities(plugin)
            self.assertNotEqual(
                metadata_only["semantic_sha256"], runtime_change["semantic_sha256"]
            )
            self.assertNotEqual(
                metadata_only["artifact_sha256"], runtime_change["artifact_sha256"]
            )


class CertificationImpactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = build_snapshot(ROOT)

    def test_snapshot_has_exact_corpus_holdout_and_package_inventory(self) -> None:
        snapshot = self.snapshot
        self.assertEqual(snapshot["schema_version"], 1)
        self.assertEqual(len(snapshot["corpus"]["cases"]), 14)
        self.assertEqual(len(snapshot["holdout"]["pairs"]), 3)
        self.assertEqual(
            snapshot["package"]["artifact_sha256"],
            "0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934",
        )

    def test_no_change_has_no_gate_or_live_call(self) -> None:
        impact = plan_impact(self.snapshot, self.snapshot)
        self.assertEqual(impact["gates"], [])
        self.assertEqual(impact["live_calls"], {"minimum": 0, "maximum": 0})
        self.assertEqual(impact["reasons"], [])

    def test_one_case_change_invalidates_only_that_corpus_case(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        case_id = sorted(changed["corpus"]["cases"])[0]
        changed["corpus"]["cases"][case_id] = "f" * 64

        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["corpus_cases"], [case_id])
        self.assertEqual(impact["holdout_pairs"], [])
        self.assertEqual(impact["gates"], ["corpus"])
        self.assertEqual(impact["live_calls"], {"minimum": 1, "maximum": 1})

    def test_shared_semantic_or_harness_change_fails_closed(self) -> None:
        for category in ("semantic", "harness"):
            with self.subTest(category=category):
                changed = copy.deepcopy(self.snapshot)
                changed["engine"]["categories"][category] = "e" * 64
                if category == "harness":
                    changed["engine"]["scopes"]["corpus_harness"] = "d" * 64
                impact = plan_impact(self.snapshot, changed)
                self.assertEqual(len(impact["corpus_cases"]), 14)
                self.assertEqual(len(impact["holdout_pairs"]), 3)
                self.assertEqual(impact["gates"], ["corpus", "holdout"])
                self.assertEqual(impact["live_calls"], {"minimum": 18, "maximum": 20})

    def test_holdout_only_harness_change_does_not_rerun_corpus(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["harness"] = "e" * 64
        changed["engine"]["scopes"]["holdout_harness"] = "d" * 64

        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["corpus_cases"], [])
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertEqual(impact["gates"], ["holdout"])
        self.assertEqual(impact["live_calls"], {"minimum": 4, "maximum": 6})

    def test_artifact_engine_or_package_change_needs_no_model_call(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["artifact"] = "d" * 64
        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["gates"], ["receipt"])
        self.assertEqual(impact["live_calls"], {"minimum": 0, "maximum": 0})

        changed = copy.deepcopy(self.snapshot)
        changed["package"]["artifact_sha256"] = "c" * 64
        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["gates"], ["isolated_install"])
        self.assertEqual(impact["live_calls"], {"minimum": 0, "maximum": 0})

    def test_unknown_snapshot_dimension_fails_closed(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["unknown"] = {"value": True}
        with self.assertRaisesRegex(IdentityError, "unknown snapshot field"):
            plan_impact(self.snapshot, changed)

    def test_refresh_ledger_forces_full_exact_pending_scope_and_cost(self) -> None:
        ledger = load_ledger(ROOT / "evaluation" / "results" / "current.json")
        impact = plan_impact(
            ledger["snapshot"], self.snapshot, pending=ledger["pending"]
        )
        self.assertEqual(len(impact["corpus_cases"]), 14)
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertEqual(impact["live_calls"], {"minimum": 18, "maximum": 20})
        self.assertEqual(impact["cost"]["combined_tokens"]["maximum"], 637027)
        self.assertEqual(impact["cost"]["wall_seconds"]["maximum"], 3187.085)


class CertificationReceiptAndCliTests(unittest.TestCase):
    def test_refresh_required_cannot_carry_a_certification(self) -> None:
        ledger = load_ledger(ROOT / "evaluation" / "results" / "current.json")
        self.assertEqual(ledger["state"], "refresh_required")
        self.assertIsNone(ledger["certification"])
        validate_ledger(ledger)

        invalid = copy.deepcopy(ledger)
        invalid["state"] = "certified"
        with self.assertRaisesRegex(ValueError, "certified ledger"):
            validate_ledger(invalid)

    def test_verify_and_impact_commands_are_read_only_json(self) -> None:
        for command in ("verify", "impact"):
            completed = subprocess.run(
                [sys.executable, "-m", "evaluation.cli", command],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["schema_version"], 1)

    def test_live_command_requires_the_exact_impact_token(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "evaluation.cli",
                    "corpus",
                    "--case",
                    "receipt-mismatch",
                    "--output",
                    str(Path(raw) / "results"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("exact approval_token", completed.stderr)


if __name__ == "__main__":
    unittest.main()
