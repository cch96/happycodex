from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from evaluation import cli, live
from evaluation.core import receipt as receipt_engine
from evaluation.core.identity import (
    IdentityError,
    canonical_sha256,
    engine_inventory,
    package_identities,
)
from evaluation.core.impact import build_snapshot, plan_impact
from evaluation.core.receipt import load_ledger, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MODULES = {
    "evaluation/__init__.py",
    "evaluation/cli.py",
    "evaluation/live.py",
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
        categories = {item["path"]: item["category"] for item in first["entries"]}
        self.assertEqual(categories["evaluation/cli.py"], "artifact")
        self.assertEqual(categories["evaluation/live.py"], "harness")
        self.assertEqual(categories["evaluation/holdout/compare.py"], "semantic")

    def test_sanitizers_live_only_in_the_artifact_module(self) -> None:
        engine = (ROOT / "evaluation/corpus/engine.py").read_text(encoding="utf-8")
        receipt = (ROOT / "evaluation/core/receipt.py").read_text(encoding="utf-8")
        for name in (
            "sanitized_recovery_receipt",
            "sanitized_result_receipt",
            "sanitized_native_compaction_receipt",
            "sanitized_case_receipt",
        ):
            self.assertNotIn(f"def {name}", engine)
            self.assertIn(f"def {name}", receipt)

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
        self.assertEqual(
            set(snapshot["settings"]["toolchain"]), {"python", "codex", "git", "rg"}
        )
        self.assertEqual(
            snapshot["engine"]["manifest_sha256"],
            engine_inventory(ROOT)["manifest_sha256"],
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

    def test_removed_case_blocks_impact_instead_of_reporting_zero_cost(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["corpus"]["cases"].pop(sorted(changed["corpus"]["cases"])[0])

        with self.assertRaisesRegex(IdentityError, "removed corpus case"):
            plan_impact(self.snapshot, changed)

    def test_removed_holdout_pair_blocks_impact(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["holdout"]["pairs"].pop(sorted(changed["holdout"]["pairs"])[0])

        with self.assertRaisesRegex(IdentityError, "exactly three pairs"):
            plan_impact(self.snapshot, changed)

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

    def test_holdout_policy_change_does_not_rerun_corpus(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["scopes"]["holdout_semantic"] = "d" * 64

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
        self.assertIsNone(ledger["live_authority"])
        validate_ledger(ledger)

        invalid = copy.deepcopy(ledger)
        invalid["state"] = "certified"
        invalid["pending"] = {
            "reasons": [],
            "corpus_cases": [],
            "holdout_pairs": [],
            "review": False,
        }
        invalid["certification"] = {}
        with self.assertRaisesRegex(ValueError, "certification receipt"):
            validate_ledger(invalid)

    def test_user_authority_is_exact_and_invocation_bound(self) -> None:
        invocation = {
            "command": "corpus",
            "package_semantic_sha256": "1" * 64,
            "package_artifact_sha256": "2" * 64,
            "model": "gpt-5.6-sol",
            "effort": "high",
            "timeout_seconds": 300,
            "arm": "candidate",
            "cases": ["receipt-mismatch"],
        }
        impact_sha256 = "3" * 64
        authority = {
            "schema_version": 1,
            "source": "current-task/user/approve-exact-cost",
            "source_sha256": "4" * 64,
            "impact_sha256": impact_sha256,
            "invocations": [invocation],
        }
        receipt_engine.validate_live_authority(authority)
        receipt_engine.require_authorized_invocation(
            authority, impact_sha256=impact_sha256, invocation=invocation
        )
        for field, value in (
            ("model", "unapproved-model"),
            ("effort", "low"),
            ("timeout_seconds", 1),
            ("package_artifact_sha256", "5" * 64),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(invocation)
                changed[field] = value
                with self.assertRaisesRegex(ValueError, "invocation is not authorized"):
                    receipt_engine.require_authorized_invocation(
                        authority,
                        impact_sha256=impact_sha256,
                        invocation=changed,
                    )

    def test_persisting_authority_does_not_create_a_token_cycle(self) -> None:
        ledger, current, impact = live.load_state()
        token = live.impact_token(ledger, current, impact)
        authorized = copy.deepcopy(ledger)
        authorized["live_authority"] = {
            "schema_version": 1,
            "source": "current-task/user/approve-exact-cost",
            "source_sha256": "4" * 64,
            "impact_sha256": token,
            "invocations": [
                {
                    "command": "corpus",
                    "package_semantic_sha256": current["package"]["semantic_sha256"],
                    "package_artifact_sha256": current["package"]["artifact_sha256"],
                    "model": current["settings"]["model"],
                    "effort": current["settings"]["effort"],
                    "timeout_seconds": current["settings"]["timeout_seconds"],
                    "arm": "candidate",
                    "cases": impact["corpus_cases"],
                }
            ],
        }
        validate_ledger(authorized)
        self.assertEqual(live.impact_token(authorized, current, impact), token)

    def test_certified_state_requires_a_digest_bound_successor_receipt(self) -> None:
        ledger = load_ledger(ROOT / "evaluation" / "results" / "current.json")
        authority = {
            "schema_version": 1,
            "source": "current-task/user/approve-exact-cost",
            "source_sha256": "4" * 64,
            "impact_sha256": "5" * 64,
            "invocations": [
                {
                    "command": "corpus",
                    "package_semantic_sha256": ledger["snapshot"]["package"][
                        "semantic_sha256"
                    ],
                    "package_artifact_sha256": ledger["snapshot"]["package"][
                        "artifact_sha256"
                    ],
                    "model": ledger["snapshot"]["settings"]["model"],
                    "effort": ledger["snapshot"]["settings"]["effort"],
                    "timeout_seconds": ledger["snapshot"]["settings"][
                        "timeout_seconds"
                    ],
                    "arm": "candidate",
                    "cases": ledger["pending"]["corpus_cases"],
                }
            ],
        }
        certified = copy.deepcopy(ledger)
        certified["state"] = "certified"
        certified["pending"] = {
            "reasons": [],
            "corpus_cases": [],
            "holdout_pairs": [],
            "review": False,
        }
        certified["live_authority"] = authority
        certified["certification"] = {
            "schema_version": 1,
            "successor_source_commit": "6" * 40,
            "successor_source_tree": "7" * 40,
            "snapshot_sha256": canonical_sha256(certified["snapshot"]),
            "engine_manifest_sha256": certified["snapshot"]["engine"][
                "manifest_sha256"
            ],
            "corpus_receipt_sha256": "8" * 64,
            "holdout_receipt_sha256": "9" * 64,
            "review_receipt_sha256": "a" * 64,
            "live_authority_sha256": canonical_sha256(authority),
        }
        validate_ledger(certified)

        invalid = copy.deepcopy(certified)
        invalid["certification"]["engine_manifest_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "engine manifest mismatch"):
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
            if command == "impact":
                self.assertFalse(payload["live_authority_ready"])
                self.assertEqual(
                    [item["command"] for item in payload["proposed_invocations"]],
                    ["corpus"],
                )
                self.assertRegex(payload["impact_token"], r"^[0-9a-f]{64}$")

    def test_impact_token_cannot_self_authorize_a_live_command(self) -> None:
        ledger, current, impact = live.load_state()
        token = live.impact_token(ledger, current, impact)
        with tempfile.TemporaryDirectory() as raw:
            with mock.patch.object(live.corpus_engine, "run_command") as runner:
                with self.assertRaisesRegex(SystemExit, "2"):
                    cli.main(
                        [
                            "corpus",
                            "--output",
                            str(Path(raw) / "results"),
                            "--bind-impact",
                            token,
                        ]
                    )
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
