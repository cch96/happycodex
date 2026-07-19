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
    sha256_bytes,
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
    "evaluation/core/ledger.py",
    "evaluation/core/receipt.py",
    "evaluation/corpus/__init__.py",
    "evaluation/corpus/contract.py",
    "evaluation/corpus/engine.py",
    "evaluation/holdout/__init__.py",
    "evaluation/holdout/blind.py",
    "evaluation/holdout/compare.py",
    "evaluation/holdout/engine.py",
}


def complete_live_authority(
    ledger: dict[str, object],
    current: dict[str, object],
    impact: dict[str, object],
) -> dict[str, object]:
    settings = current["settings"]
    package = current["package"]
    invocations: list[dict[str, object]] = []
    if impact["corpus_cases"]:
        invocations.append(
            {
                "command": "corpus",
                "package_semantic_sha256": package["semantic_sha256"],
                "package_artifact_sha256": package["artifact_sha256"],
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "arm": "candidate",
                "cases": impact["corpus_cases"],
            }
        )
    if impact["holdout_pairs"]:
        invocations.append(
            {
                "command": "holdout",
                "candidate_semantic_sha256": package["semantic_sha256"],
                "candidate_artifact_sha256": package["artifact_sha256"],
                "public_semantic_sha256": "fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4",
                "public_artifact_sha256": "77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89",
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "pairs": impact["holdout_pairs"],
            }
        )
    token = live.impact_token(ledger, current, impact)
    snapshot_sha256 = canonical_sha256(current)
    response = "批准\n"
    request = {
        "schema_version": 1,
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
    }
    return {
        "schema_version": 1,
        "source": "current-task/user/approve-exact-cost",
        "approval_request_sha256": canonical_sha256(request),
        "approval_response": response,
        "approval_response_sha256": sha256_bytes(response.encode()),
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
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
        self.assertEqual(categories["evaluation/cli.py"], "harness")
        self.assertEqual(categories["evaluation/live.py"], "harness")
        self.assertEqual(categories["evaluation/core/impact.py"], "harness")
        self.assertEqual(categories["evaluation/core/ledger.py"], "harness")
        self.assertEqual(categories["evaluation/core/receipt.py"], "artifact")
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
        python = snapshot["settings"]["toolchain"]["python"]
        self.assertRegex(python["stdlib_sha256"], r"^[0-9a-f]{64}$")
        self.assertGreater(python["stdlib_file_count"], 0)
        self.assertRegex(python["shared_libraries_sha256"], r"^[0-9a-f]{64}$")
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

    def test_real_control_mutations_fail_closed_but_sanitizer_is_artifact(self) -> None:
        for relative, expected_calls in (
            ("evaluation/cli.py", {"minimum": 18, "maximum": 20}),
            ("evaluation/core/impact.py", {"minimum": 18, "maximum": 20}),
            ("evaluation/core/ledger.py", {"minimum": 18, "maximum": 20}),
            ("evaluation/core/receipt.py", {"minimum": 0, "maximum": 0}),
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as raw:
                clone = Path(raw) / "repo"
                shutil.copytree(ROOT / "evaluation", clone / "evaluation")
                for package_path in (".agents", ".codex-plugin", "README.md", "skills"):
                    source = ROOT / package_path
                    target = clone / package_path
                    if source.is_dir():
                        shutil.copytree(source, target)
                    else:
                        shutil.copy2(source, target)
                baseline = build_snapshot(clone)
                path = clone / relative
                path.write_text(
                    path.read_text(encoding="utf-8") + "\n", encoding="utf-8"
                )
                impact = plan_impact(baseline, build_snapshot(clone))
                self.assertEqual(impact["live_calls"], expected_calls)
                if relative.endswith("receipt.py"):
                    self.assertEqual(impact["gates"], ["receipt"])
                else:
                    self.assertEqual(impact["gates"][:2], ["corpus", "holdout"])

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
        ledger, current, impact = live.load_state()
        authority = complete_live_authority(ledger, current, impact)
        invocation = authority["invocations"][0]
        receipt_engine.validate_live_authority(authority, snapshot=current)
        receipt_engine.require_authorized_invocation(
            authority, snapshot=current, impact=impact, invocation=invocation
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
                        snapshot=current,
                        impact=impact,
                        invocation=changed,
                    )

        incomplete = copy.deepcopy(authority)
        incomplete["invocations"] = incomplete["invocations"][:1]
        with self.assertRaisesRegex(ValueError, "complete impact scope"):
            receipt_engine.validate_live_authority(incomplete, snapshot=current)

        fabricated = copy.deepcopy(authority)
        fabricated["approval_response"] = "not the approved response"
        with self.assertRaisesRegex(ValueError, "approval response"):
            receipt_engine.validate_live_authority(fabricated, snapshot=current)

    def test_persisting_authority_does_not_create_a_token_cycle(self) -> None:
        ledger, current, impact = live.load_state()
        token = live.impact_token(ledger, current, impact)
        authorized = copy.deepcopy(ledger)
        authorized["live_authority"] = complete_live_authority(ledger, current, impact)
        validate_ledger(authorized)
        self.assertEqual(live.impact_token(authorized, current, impact), token)

    def test_certified_state_requires_a_digest_bound_successor_receipt(self) -> None:
        ledger = load_ledger(ROOT / "evaluation" / "results" / "current.json")
        current = build_snapshot(ROOT)
        impact = plan_impact(ledger["snapshot"], current, pending=ledger["pending"])
        authority = complete_live_authority(ledger, current, impact)
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
            "evidence": {
                name: {
                    "commit": "8" * 40,
                    "path": f"evaluation/results/evidence/{name}.json",
                    "git_blob": "9" * 40,
                    "sha256": "a" * 64,
                }
                for name in (
                    "corpus_summary",
                    "holdout_run",
                    "holdout_summary",
                    "review",
                )
            },
            "live_authority_sha256": canonical_sha256(authority),
        }
        with self.assertRaisesRegex(ValueError, "reachable certification evidence"):
            validate_ledger(certified, repo=ROOT)

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
