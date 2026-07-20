from __future__ import annotations

import copy
import json
from pathlib import Path
import pickle
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from evaluation import cli, live
from evaluation.core import ledger as ledger_engine
from evaluation.core.identity import (
    IdentityError,
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    package_identities,
    sha256_bytes,
)
from evaluation.core.impact import (
    CORPUS_MODEL_CALLS,
    build_snapshot,
    historical_cost_receipt,
    plan_impact,
)
from evaluation.core.ledger import ledger_sha256, validate_ledger
from evaluation.core.receipt import sanitized_case_receipt
from evaluation.corpus import engine as corpus_engine
from evaluation.corpus.contract import (
    FILESYSTEM_ISOLATION_POLICY,
    RECOVERY_GATE_FIELDS,
)
from evaluation.holdout import engine as holdout_engine


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
    request = {
        "schema_version": 1,
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
    }
    request_sha256 = canonical_sha256(request)
    response = ledger_engine.affirmative_approval_response(request_sha256)
    return {
        "schema_version": 1,
        "source": "current-task/user/approve-exact-cost",
        "approval_request_sha256": request_sha256,
        "approval_response": response,
        "approval_response_sha256": sha256_bytes(response.encode()),
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
    }


def refreshed_coverage(snapshot: dict[str, object]) -> dict[str, object]:
    return {
        "corpus": {case_id: "refreshed" for case_id in snapshot["corpus"]["cases"]},
        "holdout": {pair_id: "refreshed" for pair_id in snapshot["holdout"]["pairs"]},
    }


def full_live_test_state() -> tuple[
    dict[str, object], dict[str, object], dict[str, object]
]:
    current = build_snapshot(ROOT)
    pending = {
        "reasons": ["test-full-live-refresh"],
        "corpus_cases": sorted(current["corpus"]["cases"]),
        "holdout_pairs": sorted(current["holdout"]["pairs"]),
        "review": True,
    }
    ledger = {
        "schema_version": 1,
        "state": "refresh_required",
        "snapshot": current,
        "prior_evidence": {
            "source_commit": "0" * 40,
            "source_path": "evaluation/results/current.json",
            "sha256": "0" * 64,
        },
        "pending": pending,
        "historical_cost": historical_cost_receipt(),
        "live_authority": None,
        "certification": None,
    }
    impact = plan_impact(current, current, pending=pending)
    validate_ledger(ledger, repo=ROOT)
    return ledger, current, impact


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

    def test_inventory_excludes_certification_evidence_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            baseline = engine_inventory(clone)
            evidence = clone / "evaluation" / "results" / "evidence"
            evidence.mkdir(exist_ok=True)
            for name in (
                "corpus_summary",
                "holdout_run",
                "holdout_summary",
                "review",
            ):
                (evidence / f"{name}.json").write_text("{}\n", encoding="utf-8")

            self.assertEqual(engine_inventory(clone), baseline)

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
            "ace7f39fd61341e5d4b1bc3b268fd89a1562acaaacb80d7456c2bb97fb9c497e",
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

    def test_native_case_counts_initial_resume_and_fresh_model_calls(self) -> None:
        cases = corpus_engine.load_cases(ROOT / "evaluation" / "cases")
        native_cases = {
            case_id
            for case_id, case in cases.items()
            if case["fixture"].get("native_compaction_resume") is not None
        }
        self.assertEqual(
            {case_id for case_id, calls in CORPUS_MODEL_CALLS.items() if calls > 1},
            native_cases,
        )
        impact = plan_impact(
            self.snapshot,
            self.snapshot,
            pending={
                "reasons": ["native-proof-required"],
                "corpus_cases": ["pre-freeze-compaction"],
                "holdout_pairs": [],
                "review": False,
            },
        )
        self.assertEqual(impact["live_calls"], {"minimum": 3, "maximum": 3})

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
                self.assertEqual(impact["live_calls"], {"minimum": 20, "maximum": 22})

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

    def test_partial_pending_holdout_expands_to_the_executable_adaptive_scope(
        self,
    ) -> None:
        pair_id = sorted(self.snapshot["holdout"]["pairs"])[0]
        impact = plan_impact(
            self.snapshot,
            self.snapshot,
            pending={
                "reasons": ["pending-pair"],
                "corpus_cases": [],
                "holdout_pairs": [pair_id],
                "review": False,
            },
        )
        self.assertEqual(
            impact["holdout_pairs"], sorted(self.snapshot["holdout"]["pairs"])
        )
        self.assertEqual(impact["live_calls"], {"minimum": 4, "maximum": 6})

    def test_artifact_engine_or_package_change_needs_no_model_call(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["artifact"] = "d" * 64
        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["gates"], ["receipt"])
        self.assertEqual(impact["live_calls"], {"minimum": 0, "maximum": 0})

    def test_real_control_mutations_fail_closed_but_sanitizer_is_artifact(self) -> None:
        for relative, expected_calls in (
            ("evaluation/cli.py", {"minimum": 20, "maximum": 22}),
            ("evaluation/core/impact.py", {"minimum": 20, "maximum": 22}),
            ("evaluation/core/ledger.py", {"minimum": 20, "maximum": 22}),
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

    def test_impact_rejects_the_same_malformed_case_as_execution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            for package_path in (".agents", ".codex-plugin", "README.md", "skills"):
                source = ROOT / package_path
                target = clone / package_path
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
            case_path = next((clone / "evaluation" / "cases").glob("*.json"))
            malformed = json.loads(case_path.read_text(encoding="utf-8"))
            malformed.pop("oracle")
            case_path.write_text(
                json.dumps(malformed, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(IdentityError, "invalid case envelope"):
                build_snapshot(clone)

    def test_impact_rejects_the_same_malformed_holdout_as_execution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            for package_path in (".agents", ".codex-plugin", "README.md", "skills"):
                source = ROOT / package_path
                target = clone / package_path
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
            manifest_path = clone / "evaluation" / "holdouts" / "manifest.json"
            malformed = json.loads(manifest_path.read_text(encoding="utf-8"))
            malformed["pairs"][0].pop("oracle_kind")
            manifest_path.write_text(
                json.dumps(malformed, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(IdentityError, "holdout pair envelope"):
                build_snapshot(clone)

    def test_unknown_snapshot_dimension_fails_closed(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["unknown"] = {"value": True}
        with self.assertRaisesRegex(IdentityError, "unknown snapshot field"):
            plan_impact(self.snapshot, changed)

    def test_refresh_ledger_forces_full_exact_pending_scope_and_cost(self) -> None:
        ledger, current, impact = full_live_test_state()
        self.assertEqual(current, self.snapshot)
        self.assertEqual(len(impact["corpus_cases"]), 14)
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertEqual(impact["live_calls"], {"minimum": 20, "maximum": 22})
        self.assertEqual(impact["cost"]["combined_tokens"]["maximum"], 637027)
        self.assertEqual(impact["cost"]["wall_seconds"]["maximum"], 3187.085)
        self.assertEqual(
            impact["cost"]["provenance"]["holdout_summary_sha256"],
            "f301f23d0d841deaef538cf07d9fba36705ebb175a3a1e4f099bb68cfc91ea3d",
        )

        invalid = copy.deepcopy(ledger)
        invalid["historical_cost"] = {}
        with self.assertRaisesRegex(ValueError, "historical cost"):
            validate_ledger(invalid, repo=ROOT)


class CertificationReceiptAndCliTests(unittest.TestCase):
    def test_native_review_remains_an_external_completion_gate(self) -> None:
        self.assertNotIn("review", ledger_engine.COVERAGE_FIELDS)
        self.assertFalse(hasattr(ledger_engine, "_validate_review_receipt"))

    def test_refresh_required_cannot_carry_a_certification(self) -> None:
        ledger, _current, _impact = full_live_test_state()
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
        ledger, current, impact = full_live_test_state()
        authority = complete_live_authority(ledger, current, impact)
        invocation = authority["invocations"][0]
        ledger_engine.validate_live_authority(authority, snapshot=current)
        ledger_engine.require_authorized_invocation(
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
                    ledger_engine.require_authorized_invocation(
                        authority,
                        snapshot=current,
                        impact=impact,
                        invocation=changed,
                    )

        incomplete = copy.deepcopy(authority)
        incomplete["invocations"] = incomplete["invocations"][:1]
        with self.assertRaisesRegex(ValueError, "complete impact scope"):
            ledger_engine.validate_live_authority(incomplete, snapshot=current)

        fabricated = copy.deepcopy(authority)
        fabricated["approval_response"] = "not the approved response"
        with self.assertRaisesRegex(ValueError, "approval response"):
            ledger_engine.validate_live_authority(fabricated, snapshot=current)

        rejecting = copy.deepcopy(authority)
        rejecting["approval_response"] = (
            "I explicitly reject every proposed call and cost.\n"
        )
        rejecting["approval_response_sha256"] = sha256_bytes(
            rejecting["approval_response"].encode()
        )
        with self.assertRaisesRegex(ValueError, "affirmative|approval response"):
            ledger_engine.validate_live_authority(rejecting, snapshot=current)

    def test_persisting_authority_does_not_create_a_token_cycle(self) -> None:
        ledger, current, impact = full_live_test_state()
        token = live.impact_token(ledger, current, impact)
        authorized = copy.deepcopy(ledger)
        authorized["live_authority"] = complete_live_authority(ledger, current, impact)
        validate_ledger(authorized)
        self.assertEqual(live.impact_token(authorized, current, impact), token)

    def test_live_dispatch_binds_authority_digest_into_runner_args(self) -> None:
        ledger, current, impact = full_live_test_state()
        ledger["live_authority"] = complete_live_authority(ledger, current, impact)
        parser = cli.build_parser()
        args = parser.parse_args(
            [
                "corpus",
                "--bind-impact",
                live.impact_token(ledger, current, impact),
                "--output",
                "/tmp/happycodex-binding-test",
            ]
        )
        with (
            mock.patch.object(
                live, "load_state", return_value=(ledger, current, impact)
            ),
            mock.patch.object(
                live.corpus_engine, "run_authorized", return_value=0
            ) as runner,
        ):
            self.assertEqual(live.run_command(args, parser), 0)
        authorization = runner.call_args.args[1]
        self.assertIsInstance(authorization, ledger_engine.AuthorizedInvocation)
        self.assertEqual(authorization.command, "corpus")
        self.assertEqual(
            authorization.impact_token, ledger["live_authority"]["impact_token"]
        )
        self.assertEqual(
            authorization.authority_sha256, canonical_sha256(ledger["live_authority"])
        )
        self.assertFalse(hasattr(ledger_engine, "_AUTHORIZATION_SEAL"))
        with self.assertRaisesRegex(TypeError, "validator-minted"):
            ledger_engine.AuthorizedInvocation()
        descriptor = authorization.descriptor()
        descriptor["cases"] = []
        self.assertNotEqual(descriptor, authorization.descriptor())
        with self.assertRaises((AttributeError, TypeError)):
            authorization.impact_token = "f" * 64
        with self.assertRaises(AttributeError):
            authorization._descriptor  # type: ignore[attr-defined]
        with self.assertRaisesRegex(TypeError, "cannot be copied"):
            copy.copy(authorization)
        with self.assertRaisesRegex(TypeError, "cannot be copied"):
            copy.deepcopy(authorization)
        with self.assertRaisesRegex(TypeError, "cannot be serialized"):
            pickle.dumps(authorization)

    def test_model_reaching_helpers_require_authorized_capability(self) -> None:
        case = corpus_engine.load_cases()["receipt-mismatch"]
        with tempfile.TemporaryDirectory() as raw:
            with mock.patch.object(
                corpus_engine,
                "build_fixture",
                side_effect=AssertionError("corpus live seam reached"),
            ) as fixture:
                with self.assertRaisesRegex(ValueError, "capability"):
                    corpus_engine.evaluate_case(
                        case,
                        plugin=ROOT,
                        output=Path(raw),
                        model="gpt-5.6-sol",
                        effort="high",
                        timeout=300,
                        arm="candidate",
                    )
            fixture.assert_not_called()

            with mock.patch.object(
                corpus_engine,
                "run",
                side_effect=AssertionError("Codex invocation reached"),
            ) as runner:
                with self.assertRaisesRegex(ValueError, "capability"):
                    corpus_engine.invoke_codex(
                        ["codex", "exec"],
                        cwd=Path(raw),
                        env={},
                        timeout=1,
                    )
            runner.assert_not_called()

    def test_offline_summary_requires_exact_gate_evidence(self) -> None:
        snapshot = build_snapshot(ROOT)
        installation = {
            "source_skill_sha256": "1" * 64,
            "installed_skill_sha256": "1" * 64,
            "source_package_manifest_sha256": snapshot["package"]["artifact_sha256"],
            "installed_package_manifest_sha256": snapshot["package"]["artifact_sha256"],
            "plugin_sha256": "2" * 64,
        }
        payload = {
            "schema_version": 1,
            "engine_generation": "0.4",
            "source_commit": "3" * 40,
            "source_ledger_sha256": "4" * 64,
            "snapshot_sha256": canonical_sha256(snapshot),
            "engine_manifest_sha256": snapshot["engine"]["manifest_sha256"],
            "gates": ["isolated_install", "receipt"],
            "receipt_artifact_sha256": snapshot["engine"]["categories"]["artifact"],
            "isolated_installation": installation,
        }
        ledger_engine._validate_offline_summary(
            payload,
            snapshot=snapshot,
            source_commit="3" * 40,
            source_ledger_sha256="4" * 64,
            gates={"isolated_install", "receipt"},
        )

        missing_installation = copy.deepcopy(payload)
        missing_installation["isolated_installation"] = None
        with self.assertRaisesRegex(ValueError, "installation"):
            ledger_engine._validate_offline_summary(
                missing_installation,
                snapshot=snapshot,
                source_commit="3" * 40,
                source_ledger_sha256="4" * 64,
                gates={"isolated_install", "receipt"},
            )

    def test_leaf_runner_commands_reject_fabricated_live_bindings(self) -> None:
        parser = cli.build_parser()
        with tempfile.TemporaryDirectory() as raw:
            corpus_args = parser.parse_args(
                [
                    "corpus",
                    "--case",
                    "receipt-mismatch",
                    "--output",
                    str(Path(raw) / "corpus"),
                    "--bind-impact",
                    "a" * 64,
                ]
            )
            corpus_args.live_authority_sha256 = "b" * 64
            with mock.patch.object(
                corpus_engine,
                "evaluate_case",
                side_effect=AssertionError("corpus evaluator reached"),
            ) as evaluator:
                with self.assertRaisesRegex(SystemExit, "evaluation.cli"):
                    corpus_engine.run_command(corpus_args)
            evaluator.assert_not_called()

            ledger, current, impact = full_live_test_state()
            authority = complete_live_authority(ledger, current, impact)
            corpus_invocation = next(
                item for item in authority["invocations"] if item["command"] == "corpus"
            )
            authorization = ledger_engine.require_authorized_invocation(
                authority,
                snapshot=current,
                impact=impact,
                invocation=corpus_invocation,
            )
            mismatched_plugin = Path(raw) / "mismatched-plugin"
            mismatched_plugin.mkdir()
            mismatched_args = parser.parse_args(
                [
                    "corpus",
                    "--plugin",
                    str(mismatched_plugin),
                    "--output",
                    str(Path(raw) / "mismatched-corpus"),
                ]
            )
            with mock.patch.object(
                corpus_engine,
                "evaluate_case",
                side_effect=AssertionError("corpus evaluator reached"),
            ) as evaluator:
                with self.assertRaisesRegex(SystemExit, "package"):
                    corpus_engine.run_authorized(mismatched_args, authorization)
            evaluator.assert_not_called()

            holdout_args = parser.parse_args(
                [
                    "holdout",
                    "--candidate",
                    str(ROOT),
                    "--public",
                    str(ROOT),
                    "--output",
                    str(Path(raw) / "holdout"),
                    "--bind-impact",
                    "a" * 64,
                ]
            )
            holdout_args.live_authority_sha256 = "b" * 64
            with mock.patch.object(
                holdout_engine,
                "run_holdouts",
                side_effect=AssertionError("holdout evaluator reached"),
            ) as runner:
                with self.assertRaisesRegex(SystemExit, "evaluation.cli"):
                    holdout_engine.run_command(holdout_args)
            runner.assert_not_called()

    def test_verify_preserves_repo_context_for_certified_ledger_hash(self) -> None:
        ledger = {"state": "certified", "live_authority": {}}
        current = {"engine": {"manifest_sha256": "a" * 64}}
        impact = {"gates": []}
        inventory = {"manifest_sha256": "a" * 64}
        with (
            mock.patch.object(
                cli.live, "load_state", return_value=(ledger, current, impact)
            ),
            mock.patch.object(cli, "engine_inventory", return_value=inventory),
            mock.patch.object(cli, "canonical_sha256", return_value="b" * 64),
            mock.patch.object(cli, "ledger_sha256", return_value="c" * 64) as digest,
            mock.patch("builtins.print"),
        ):
            self.assertEqual(cli.verify_command(), 0)
        digest.assert_called_once_with(ledger, repo=ROOT)

    def test_corpus_certification_accepts_the_exact_authorized_subset(self) -> None:
        snapshot = build_snapshot(ROOT)
        changed = copy.deepcopy(snapshot)
        case_id = sorted(changed["corpus"]["cases"])[0]
        changed["corpus"]["cases"][case_id] = "f" * 64
        impact = plan_impact(snapshot, changed)
        authority = {"impact_token": "a" * 64, "impact": impact}
        case = {
            "id": case_id,
            "uncached_input_tokens": 2,
            "usage": {"output_tokens": 1},
            "elapsed_seconds": 1.0,
        }
        payload = {
            "schema_version": 1,
            "engine_generation": "0.4",
            "impact_token": authority["impact_token"],
            "live_authority_sha256": canonical_sha256(authority),
            "arm": "candidate",
            "model": changed["settings"]["model"],
            "effort": changed["settings"]["effort"],
            "timeout_seconds": changed["settings"]["timeout_seconds"],
            "passed": 1,
            "total": 1,
            "uncached_input_tokens": 2,
            "telemetry_complete": True,
            "output_tokens": 1,
            "elapsed_seconds": 1.0,
            "cases": [case],
        }
        with mock.patch.object(ledger_engine, "_validate_case_identity") as validate:
            ledger_engine._validate_corpus_summary(
                payload,
                changed,
                {"engine": engine_inventory(ROOT)},
                authority,
            )
        validate.assert_called_once()

    def test_certified_state_requires_a_digest_bound_successor_receipt(self) -> None:
        ledger, current, impact = full_live_test_state()
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
            "coverage": refreshed_coverage(certified["snapshot"]),
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
                )
            },
            "live_authority_sha256": canonical_sha256(authority),
        }
        with self.assertRaisesRegex(ValueError, "reachable certification evidence"):
            validate_ledger(certified, repo=ROOT)

    def test_certified_state_accepts_only_reachable_bound_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            shutil.copytree(ROOT / "evaluation", repo / "evaluation")
            for package_path in (".agents", ".codex-plugin", "README.md", "skills"):
                source = ROOT / package_path
                target = repo / package_path
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)

            def git(*args: str) -> str:
                completed = subprocess.run(
                    ["git", *args],
                    cwd=repo,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return completed.stdout.strip()

            git("init", "-q")
            git("config", "user.name", "HappyCodex test")
            git("config", "user.email", "happycodex-test@example.invalid")
            git("add", ".")
            git("commit", "-qm", "source without authority")
            unauthorized_source_commit = git("rev-parse", "HEAD")
            unauthorized_source_tree = git("rev-parse", "HEAD^{tree}")

            snapshot = build_snapshot(repo)
            pending = {
                "reasons": ["engine_generation_changed"],
                "corpus_cases": sorted(snapshot["corpus"]["cases"]),
                "holdout_pairs": sorted(snapshot["holdout"]["pairs"]),
                "review": True,
            }
            impact = plan_impact(snapshot, snapshot, pending=pending)
            ledger = {
                "schema_version": 1,
                "state": "refresh_required",
                "snapshot": snapshot,
                "prior_evidence": {
                    "source_commit": unauthorized_source_commit,
                    "source_path": "evaluation/results/behavior-v21.json",
                    "sha256": "0" * 64,
                },
                "pending": pending,
                "historical_cost": historical_cost_receipt(),
                "live_authority": None,
                "certification": None,
            }
            authority = complete_live_authority(ledger, snapshot, impact)
            authorized_ledger = copy.deepcopy(ledger)
            authorized_ledger["live_authority"] = authority
            (repo / "evaluation" / "results" / "current.json").write_text(
                json.dumps(
                    authorized_ledger,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            git("add", "evaluation/results/current.json")
            git("commit", "-qm", "persist exact live authority")
            source_commit = git("rev-parse", "HEAD")
            source_tree = git("rev-parse", "HEAD^{tree}")
            git("update-index", "--chmod=+x", "skills/happycodex/SKILL.md")
            git("commit", "-qm", "source with package mode drift")
            mode_drift_source_commit = git("rev-parse", "HEAD")
            mode_drift_source_tree = git("rev-parse", "HEAD^{tree}")
            git("update-index", "--chmod=-x", "skills/happycodex/SKILL.md")
            settings = snapshot["settings"]
            engine_identity = engine_inventory(repo)
            source_cases = corpus_engine.load_cases(repo / "evaluation" / "cases")
            native_fixture_evidence: dict[str, dict[str, object]] = {}
            for case_id, source_case in source_cases.items():
                native = source_case["fixture"].get("native_compaction_resume")
                if native is None:
                    continue
                fixture_repo = Path(raw) / f"native-fixture-{case_id}"
                fixture = corpus_engine.build_fixture(source_case, fixture_repo)
                transition = corpus_engine.apply_post_compaction_transition(
                    fixture_repo, native["post_compaction_transition"], fixture
                )
                native_fixture_evidence[case_id] = {
                    "recovery_state": corpus_engine.expected_recovery_state(
                        native, fixture, transition
                    ),
                    "post_compaction_transition_sha256": canonical_sha256(transition),
                    "transition": transition,
                }
            native_evidence_oracles = {
                case_id: {
                    key: value for key, value in evidence.items() if key != "transition"
                }
                for case_id, evidence in native_fixture_evidence.items()
            }

            def case_receipt(
                case_id: str,
                semantic_sha256: str,
                package: dict[str, str],
                case_descriptor: dict[str, object] | None = None,
            ) -> dict[str, object]:
                case = case_descriptor or source_cases.get(case_id)
                self.assertIsInstance(case, dict)
                native = (
                    case["fixture"].get("native_compaction_resume")
                    if isinstance(case, dict)
                    else None
                )
                phase = {
                    "input_tokens": 2,
                    "cached_input_tokens": 0,
                    "output_tokens": 1,
                    "reasoning_output_tokens": 0,
                }
                phase_count = 3 if native else 1
                usage_phases = [copy.deepcopy(phase) for _ in range(phase_count)]
                usage = {key: value * phase_count for key, value in phase.items()}
                recovery_state = (
                    copy.deepcopy(native_fixture_evidence[case_id]["recovery_state"])
                    if native
                    else None
                )
                expected = {
                    field: values[0] if isinstance(values, list) else values
                    for field, values in case["oracle"]["expected"].items()
                }
                findings = []
                blockers = []
                for required in case["oracle"].get("required_classifications", []):
                    states = required["state"]
                    findings.append(
                        {
                            "identity": required["identity"],
                            "domain": required["domain"],
                            "state": states[0] if isinstance(states, list) else states,
                            "anchors": [],
                        }
                    )
                for index, required in enumerate(
                    case["oracle"].get("required_anchored_classifications", [])
                ):
                    states = required["state"]
                    findings.append(
                        {
                            "identity": f"anchored-classification-{index}",
                            "domain": required["domain"],
                            "state": states[0] if isinstance(states, list) else states,
                            "anchors": [required["anchor"]],
                        }
                    )
                for index, required in enumerate(
                    case["oracle"].get("required_anchored_blockers", [])
                ):
                    identity = f"anchored-blocker-{index}"
                    classes = required["class"]
                    findings.append(
                        {
                            "identity": identity,
                            "domain": "other",
                            "state": "candidate_new",
                            "anchors": [required["anchor"]],
                        }
                    )
                    blockers.append(
                        {
                            "identity": identity,
                            "class": classes[0]
                            if isinstance(classes, list)
                            else classes,
                            "blocking": True,
                            "reason": "required by the case oracle",
                        }
                    )
                open_gates = (
                    ["Run /goal pause before ending at the user gate."]
                    if corpus_engine.fixture_requires_goal_pause_handoff(
                        case["fixture"]
                    )
                    and expected["decision"] == "stop_for_user"
                    else []
                )
                result = {
                    **expected,
                    "finding_classifications": findings,
                    "blocker_classifications": blockers,
                    "open_gates": open_gates,
                    "evidence": [],
                    "reason": "",
                    "recovery_state": recovery_state,
                }
                self.assertEqual(
                    corpus_engine.match_oracle(
                        result,
                        case["oracle"],
                        expected_recovery_state=recovery_state if native else None,
                        fixture=case["fixture"],
                    ),
                    [],
                )
                compaction_phase = {
                    "rollout_path": ".codex/sessions/native.jsonl",
                    "rollout_sha256": "7" * 64,
                    "rollout_byte_count": 128,
                    "rollout_prefix_sha256": None,
                    "compaction_event_count": 1,
                    "context_compacted_marker_count": 0,
                    "event_types": ["compacted"],
                    "rollout_match_count": 1,
                }
                native_compaction = (
                    {
                        "auto_compact_token_limit": native["auto_compact_token_limit"],
                        "before_resume": copy.deepcopy(compaction_phase),
                        "compaction_event_count": 1,
                        "resumed_same_thread": True,
                        "post_compaction_transition": copy.deepcopy(
                            native_fixture_evidence[case_id]["transition"]
                        ),
                        "after_resume": {
                            **copy.deepcopy(compaction_phase),
                            "rollout_sha256": "6" * 64,
                            "rollout_byte_count": 256,
                            "rollout_prefix_sha256": "7" * 64,
                        },
                        "fresh_control": {
                            "thread_id": "fresh-thread",
                            "distinct_from_resumed_task": True,
                            "no_resume_handle": True,
                            "no_conversation_summary": True,
                            "prompt_sha256": "8" * 64,
                            "equivalent_gate_fields": [
                                *sorted(RECOVERY_GATE_FIELDS),
                                "recovery_state",
                            ],
                            "allowed_label_differences": {},
                        },
                    }
                    if native
                    else None
                )
                raw_receipt = {
                    "case": case_id,
                    "installation": {
                        "source_skill_sha256": "1" * 64,
                        "installed_skill_sha256": "1" * 64,
                        "source_package_manifest_sha256": package["artifact_sha256"],
                        "installed_package_manifest_sha256": package["artifact_sha256"],
                        "plugin": {"installedPath": "/isolated/plugin"},
                    },
                    "model": settings["model"],
                    "effort": settings["effort"],
                    "timeout_seconds": settings["timeout_seconds"],
                    "timed_out": False,
                    "elapsed_seconds": 1.0,
                    "exit_code": 0,
                    "semantic_input_sha256": semantic_sha256,
                    "identities": {
                        "engine": engine_identity,
                        "package": package,
                        "toolchain": settings["toolchain"],
                    },
                    "events_sha256": "2" * 64,
                    "stderr_sha256": "3" * 64,
                    "usage": usage,
                    "usage_phases": usage_phases,
                    "uncached_input_tokens": 2 * phase_count,
                    "passed": True,
                    "result": result,
                    "fresh_recovery_result": copy.deepcopy(result) if native else None,
                    "oracle_failures": [],
                    "native_compaction": native_compaction,
                    "thread_id": "primary-thread",
                    "resume_thread_id": "primary-thread" if native else None,
                    "fresh_recovery_thread_id": "fresh-thread" if native else None,
                    "filesystem_isolation": {
                        **FILESYSTEM_ISOLATION_POLICY,
                        "workspace_root": "<case-temp>/repo",
                        "native_tool_root": "<case-temp>/bin",
                    },
                }
                return sanitized_case_receipt(
                    raw_receipt,
                    metadata_sha256="0" * 64,
                )

            corpus_cases = [
                case_receipt(case_id, semantic_sha256, snapshot["package"])
                for case_id, semantic_sha256 in snapshot["corpus"]["cases"].items()
            ]
            corpus_summary = {
                "schema_version": 1,
                "engine_generation": "0.4",
                "impact_token": authority["impact_token"],
                "live_authority_sha256": canonical_sha256(authority),
                "arm": "candidate",
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "passed": len(snapshot["corpus"]["cases"]),
                "total": len(snapshot["corpus"]["cases"]),
                "uncached_input_tokens": sum(
                    item["uncached_input_tokens"] for item in corpus_cases
                ),
                "telemetry_complete": True,
                "output_tokens": sum(
                    item["usage"]["output_tokens"] for item in corpus_cases
                ),
                "elapsed_seconds": round(
                    sum(item["elapsed_seconds"] for item in corpus_cases), 3
                ),
                "cases": corpus_cases,
            }

            def retotal_corpus(summary: dict[str, object]) -> None:
                cases = summary["cases"]
                summary["uncached_input_tokens"] = sum(
                    item["uncached_input_tokens"] for item in cases
                )
                summary["output_tokens"] = sum(
                    item["usage"]["output_tokens"] for item in cases
                )
                summary["elapsed_seconds"] = round(
                    sum(item["elapsed_seconds"] for item in cases), 3
                )

            missing_native = copy.deepcopy(corpus_summary)
            native_receipt = next(
                item
                for item in missing_native["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            native_receipt["usage_phases"] = [native_receipt["usage_phases"][0]]
            native_receipt["usage"] = copy.deepcopy(native_receipt["usage_phases"][0])
            native_receipt["uncached_input_tokens"] = 2
            native_receipt["fresh_recovery_result"] = None
            native_receipt["native_compaction"] = None
            retotal_corpus(missing_native)

            mismatched_install = copy.deepcopy(corpus_summary)
            mismatched_install["cases"][0]["installation"]["installed_skill_sha256"] = (
                "f" * 64
            )

            empty_isolation = copy.deepcopy(corpus_summary)
            empty_isolation["cases"][0]["filesystem_isolation"] = {}

            empty_result = copy.deepcopy(corpus_summary)
            empty_result["cases"][0]["result"] = {}

            wrong_oracle_projection = copy.deepcopy(corpus_summary)
            wrong_oracle_projection["cases"][0]["result"][
                "protocol_may_product_write"
            ] = not wrong_oracle_projection["cases"][0]["result"][
                "protocol_may_product_write"
            ]

            forged_isolation_policy = copy.deepcopy(corpus_summary)
            forged_isolation_policy["cases"][0]["filesystem_isolation"][
                "policy_sha256"
            ] = "e" * 64

            mismatched_native_control = copy.deepcopy(corpus_summary)
            native_control = next(
                item
                for item in mismatched_native_control["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            native_control["fresh_recovery_thread_id_sha256"] = native_control[
                "thread_id_sha256"
            ]

            source_recovery_drift = copy.deepcopy(corpus_summary)
            source_recovery = next(
                item
                for item in source_recovery_drift["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            source_recovery["result"]["recovery_state"]["writer"] = "unknown"
            source_recovery["fresh_recovery_result"]["recovery_state"]["writer"] = (
                "unknown"
            )

            fresh_revision_drift = copy.deepcopy(corpus_summary)
            fresh_revision = next(
                item
                for item in fresh_revision_drift["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            fresh_revision["fresh_recovery_result"]["recovery_state"][
                "current_revision"
            ] = "e" * 40

            unrelated_after_rollout = copy.deepcopy(corpus_summary)
            unrelated_rollout = next(
                item
                for item in unrelated_after_rollout["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            unrelated_rollout["native_compaction"]["after_resume"][
                "rollout_path_sha256"
            ] = "e" * 64

            rewritten_after_rollout = copy.deepcopy(corpus_summary)
            rewritten_rollout = next(
                item
                for item in rewritten_after_rollout["cases"]
                if item["id"] == "pre-freeze-compaction"
            )
            rewritten_rollout["native_compaction"]["after_resume"][
                "rollout_prefix_sha256"
            ] = "e" * 64

            missing_required_classifications = copy.deepcopy(corpus_summary)
            classification_case = next(
                item
                for item in missing_required_classifications["cases"]
                if item["id"] == "compaction-recovery"
            )
            classification_case["result"]["finding_classifications"] = []

            missing_required_anchors = copy.deepcopy(corpus_summary)
            anchored_case = next(
                item
                for item in missing_required_anchors["cases"]
                if item["id"] == "boundary-cutover"
            )
            anchored_case["result"]["finding_classifications"] = []
            anchored_case["result"]["blocker_classifications"] = []

            missing_goal_pause_handoff = copy.deepcopy(corpus_summary)
            goal_case = next(
                item
                for item in missing_goal_pause_handoff["cases"]
                if item["id"] == "goal-divergence"
            )
            goal_case["result"]["goal_pause_handoff_present"] = False

            corpus_false_greens = (
                (
                    "missing-native-recovery",
                    missing_native,
                    "native|usage phase|evidence telemetry",
                ),
                ("mismatched-install", mismatched_install, "installation"),
                ("empty-isolation", empty_isolation, "isolation"),
                ("empty-result-envelope", empty_result, "result receipt"),
                ("wrong-oracle-projection", wrong_oracle_projection, "oracle"),
                (
                    "forged-isolation-policy",
                    forged_isolation_policy,
                    "isolation",
                ),
                (
                    "mismatched-native-control",
                    mismatched_native_control,
                    "native|thread|control",
                ),
                ("source-recovery-drift", source_recovery_drift, "recovery|oracle"),
                ("fresh-revision-drift", fresh_revision_drift, "recovery|control"),
                (
                    "unrelated-after-rollout",
                    unrelated_after_rollout,
                    "compaction|rollout",
                ),
                (
                    "rewritten-after-rollout",
                    rewritten_after_rollout,
                    "compaction|rollout|append",
                ),
                (
                    "missing-required-classifications",
                    missing_required_classifications,
                    "classification|oracle",
                ),
                (
                    "missing-required-anchors",
                    missing_required_anchors,
                    "anchor|blocker|oracle",
                ),
                (
                    "missing-goal-pause-handoff",
                    missing_goal_pause_handoff,
                    "Goal-pause|handoff|oracle",
                ),
            )
            for label, false_green, expected_error in corpus_false_greens:
                with self.subTest(corpus_false_green=label):
                    with self.assertRaisesRegex(ValueError, expected_error):
                        ledger_engine._validate_corpus_summary(
                            false_green,
                            snapshot,
                            {
                                "engine": engine_identity,
                                "corpus_cases": source_cases,
                                "native_evidence_oracles": native_evidence_oracles,
                            },
                            authority,
                        )

            holdout_binding = next(
                item
                for item in authority["invocations"]
                if item["command"] == "holdout"
            )
            public_identity = {
                "semantic_sha256": holdout_binding["public_semantic_sha256"],
                "artifact_sha256": holdout_binding["public_artifact_sha256"],
            }
            manifest_path = repo / "evaluation" / "holdouts" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_pair_ids = [row["id"] for row in manifest["pairs"]]
            descriptors: dict[str, dict[str, object]] = {}
            for row in manifest["pairs"]:
                case_path = repo / row["case_path"]
                descriptors[row["id"]] = {
                    **row,
                    "case": json.loads(case_path.read_text(encoding="utf-8")),
                    "case_sha256": sha256_bytes(case_path.read_bytes()),
                }
            holdout_run = {
                "schema_version": 1,
                "engine_generation": "0.4",
                "impact_token": authority["impact_token"],
                "live_authority_sha256": canonical_sha256(authority),
                "manifest_sha256": sha256_bytes(manifest_path.read_bytes()),
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "pair_ids": run_pair_ids,
                "case_sha256": {
                    pair_id: descriptor["case_sha256"]
                    for pair_id, descriptor in descriptors.items()
                },
                "identities": {
                    "engine": engine_identity,
                    "packages": {
                        "candidate": snapshot["package"],
                        "public-0.2": public_identity,
                    },
                    "toolchain": settings["toolchain"],
                },
            }
            metrics = {
                "uncached_input_tokens": 2,
                "output_tokens": 1,
                "elapsed_seconds": 1.0,
            }
            shared_semantic = engine_category_sha256(
                engine_identity,
                "semantic",
                paths={"evaluation/corpus/contract.py"},
            )
            pair_receipts: list[dict[str, object]] = []
            for pair_id in run_pair_ids[:2]:
                descriptor = descriptors[pair_id]
                case = descriptor["case"]
                arm_receipts = {
                    arm: case_receipt(
                        case["id"],
                        case_semantic_sha256(
                            case,
                            shared_semantic_sha256=shared_semantic,
                            package_semantic_sha256=package["semantic_sha256"],
                            model=settings["model"],
                            effort=settings["effort"],
                            timeout=settings["timeout_seconds"],
                            arm=arm,
                        ),
                        package,
                        case,
                    )
                    for arm, package in (
                        ("candidate", snapshot["package"]),
                        ("public-0.2", public_identity),
                    )
                }
                pair_receipts.append(
                    {
                        "schema_version": 1,
                        "engine_generation": "0.4",
                        "id": pair_id,
                        "case_id": case["id"],
                        "case_sha256": descriptor["case_sha256"],
                        "outside_diff_boundary": descriptor["outside_diff_boundary"],
                        "oracle_kind": descriptor["oracle_kind"],
                        "mapping_commitment_file_sha256": "7" * 64,
                        "pre_reveal_decision_file_sha256": "8" * 64,
                        "mapping_reveal_file_sha256": "9" * 64,
                        "pre_reveal_decision_sha256": "a" * 64,
                        "mapping_commitment_sha256": "b" * 64,
                        "outcome": "equal",
                        "metrics": {
                            "candidate": metrics,
                            "public-0.2": metrics,
                        },
                        "arms": arm_receipts,
                    },
                )
            evidence_root = repo / "evaluation" / "results" / "evidence"
            evidence_root.mkdir(parents=True, exist_ok=True)

            def write_evidence(name: str, value: object) -> str:
                path = evidence_root / f"{name}.json"
                encoded = (
                    json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n"
                ).encode()
                path.write_bytes(encoded)
                return sha256_bytes(encoded)

            evidence_sha = {
                "corpus_summary": write_evidence("corpus_summary", corpus_summary),
                "holdout_run": write_evidence("holdout_run", holdout_run),
            }
            holdout_summary = {
                "schema_version": 1,
                "engine_generation": "0.4",
                "run_receipt_sha256": evidence_sha["holdout_run"],
                "adaptive_history": ["equal", "equal"],
                "adaptive_terminal_action": "stop",
                "pairs_run": 2,
                "pair_receipts": pair_receipts,
                "cost_gate": ledger_engine.cost_gate(
                    {key: value * 2 for key, value in metrics.items()},
                    {key: value * 2 for key, value in metrics.items()},
                    quality="equal",
                ),
            }

            source_evidence = {
                "corpus_semantic_sha256": shared_semantic,
                "engine": engine_identity,
                "holdout_descriptors": descriptors,
                "native_evidence_oracles": native_evidence_oracles,
            }
            authentic_better = copy.deepcopy(holdout_summary)
            authentic_better["adaptive_history"] = ["better", "better"]
            for pair_receipt in authentic_better["pair_receipts"]:
                pair_receipt["outcome"] = "better"
                public_receipt = pair_receipt["arms"]["public-0.2"]
                public_receipt["passed"] = False
                public_receipt["oracle_failures"] = {
                    "count": 1,
                    "sha256": canonical_sha256(["public control failed"]),
                }
            authentic_better["cost_gate"] = ledger_engine.cost_gate(
                {key: value * 2 for key, value in metrics.items()},
                {key: value * 2 for key, value in metrics.items()},
                quality="materially_better",
            )
            ledger_engine._validate_holdout_summary(
                authentic_better,
                snapshot,
                run_pair_ids=run_pair_ids,
                run_sha256=evidence_sha["holdout_run"],
                public_package=public_identity,
                source=source_evidence,
            )

            mislabeled_better = copy.deepcopy(holdout_summary)
            mislabeled_better["adaptive_history"] = ["better", "better"]
            for pair_receipt in mislabeled_better["pair_receipts"]:
                pair_receipt["outcome"] = "better"
            mislabeled_better["cost_gate"] = ledger_engine.cost_gate(
                {key: value * 2 for key, value in metrics.items()},
                {key: value * 2 for key, value in metrics.items()},
                quality="materially_better",
            )
            with self.assertRaisesRegex(ValueError, "holdout outcome mismatch"):
                ledger_engine._validate_holdout_summary(
                    mislabeled_better,
                    snapshot,
                    run_pair_ids=run_pair_ids,
                    run_sha256=evidence_sha["holdout_run"],
                    public_package=public_identity,
                    source=source_evidence,
                )

            nonzero_exit = copy.deepcopy(holdout_summary)
            nonzero_exit["pair_receipts"][0]["arms"]["candidate"]["exit_code"] = 7

            malformed_nested = copy.deepcopy(authentic_better)
            malformed_public = malformed_nested["pair_receipts"][0]["arms"][
                "public-0.2"
            ]
            malformed_public["usage_phases"] = [None]
            malformed_public["result"] = "runner-impossible"
            malformed_public["native_compaction"] = "runner-impossible"

            timed_out_zero_exit = copy.deepcopy(authentic_better)
            timed_out_zero_exit["pair_receipts"][0]["arms"]["public-0.2"][
                "timed_out"
            ] = True

            null_result_with_usage = copy.deepcopy(authentic_better)
            null_result_with_usage["pair_receipts"][0]["arms"]["public-0.2"][
                "result"
            ] = None

            unbound_metrics = copy.deepcopy(holdout_summary)
            expensive_candidate = unbound_metrics["pair_receipts"][0]["arms"][
                "candidate"
            ]
            expensive_candidate["usage"] = {
                "input_tokens": 20,
                "cached_input_tokens": 0,
                "output_tokens": 10,
                "reasoning_output_tokens": 0,
            }
            expensive_candidate["usage_phases"] = [
                copy.deepcopy(expensive_candidate["usage"])
            ]
            expensive_candidate["uncached_input_tokens"] = 20
            expensive_candidate["elapsed_seconds"] = 10.0

            nonterminal = copy.deepcopy(holdout_summary)
            nonterminal["adaptive_history"] = ["equal"]
            nonterminal["adaptive_terminal_action"] = "run_second"
            nonterminal["pairs_run"] = 1
            nonterminal["pair_receipts"] = nonterminal["pair_receipts"][:1]
            nonterminal["cost_gate"] = ledger_engine.cost_gate(
                metrics,
                metrics,
                quality="equal",
            )

            false_greens = (
                ("nonzero-pass-exit", nonzero_exit, "infrastructure"),
                (
                    "runner-impossible-nested-receipt",
                    malformed_nested,
                    "nested receipt|evidence telemetry",
                ),
                (
                    "timed-out-zero-exit",
                    timed_out_zero_exit,
                    "infrastructure",
                ),
                (
                    "null-result-with-usage",
                    null_result_with_usage,
                    "result receipt",
                ),
                ("unbound-cost-metrics", unbound_metrics, "metrics mismatch"),
                ("nonterminal-adaptive-history", nonterminal, "not terminal"),
            )
            for label, false_green, expected_error in false_greens:
                with self.subTest(false_green=label):
                    with self.assertRaisesRegex(ValueError, expected_error):
                        ledger_engine._validate_holdout_summary(
                            false_green,
                            snapshot,
                            run_pair_ids=run_pair_ids,
                            run_sha256=evidence_sha["holdout_run"],
                            public_package=public_identity,
                            source=source_evidence,
                        )

            evidence_sha["holdout_summary"] = write_evidence(
                "holdout_summary", holdout_summary
            )
            git("add", "evaluation/results/evidence")
            git("commit", "-qm", "evidence")
            evidence_commit = git("rev-parse", "HEAD")
            locators = {
                name: {
                    "commit": evidence_commit,
                    "path": f"evaluation/results/evidence/{name}.json",
                    "git_blob": git(
                        "rev-parse",
                        f"{evidence_commit}:evaluation/results/evidence/{name}.json",
                    ),
                    "sha256": digest,
                }
                for name, digest in evidence_sha.items()
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
                "successor_source_commit": source_commit,
                "successor_source_tree": source_tree,
                "snapshot_sha256": canonical_sha256(snapshot),
                "engine_manifest_sha256": snapshot["engine"]["manifest_sha256"],
                "coverage": refreshed_coverage(snapshot),
                "evidence": locators,
                "live_authority_sha256": canonical_sha256(authority),
            }
            validate_ledger(certified, repo=repo)
            self.assertEqual(build_snapshot(repo), snapshot)

            late_authority = copy.deepcopy(certified)
            late_authority["certification"]["successor_source_commit"] = (
                unauthorized_source_commit
            )
            late_authority["certification"]["successor_source_tree"] = (
                unauthorized_source_tree
            )
            with self.assertRaisesRegex(ValueError, "source.*authority"):
                validate_ledger(late_authority, repo=repo)

            same_commit = copy.deepcopy(certified)
            same_commit["certification"]["successor_source_commit"] = evidence_commit
            same_commit["certification"]["successor_source_tree"] = git(
                "rev-parse", f"{evidence_commit}^{{tree}}"
            )
            with self.assertRaisesRegex(ValueError, "strictly postdate"):
                validate_ledger(same_commit, repo=repo)

            wrong_artifact = copy.deepcopy(certified)
            wrong_artifact["certification"]["successor_source_commit"] = (
                mode_drift_source_commit
            )
            wrong_artifact["certification"]["successor_source_tree"] = (
                mode_drift_source_tree
            )
            with self.assertRaisesRegex(ValueError, "source package"):
                validate_ledger(wrong_artifact, repo=repo)

            prior_path = repo / "evaluation" / "results" / "current.json"
            prior_encoded = (
                json.dumps(certified, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode()
            prior_path.write_bytes(prior_encoded)
            git("add", "evaluation/results/current.json")
            git("commit", "-qm", "persist first certified ledger")
            prior_commit = git("rev-parse", "HEAD")

            changed_case_path = (
                repo
                / "evaluation"
                / "cases"
                / (sorted(snapshot["corpus"]["cases"])[0] + ".json")
            )
            changed_case = json.loads(changed_case_path.read_text(encoding="utf-8"))
            changed_case["prompt"] += "\nReconfirm the exact bounded outcome."
            changed_case_path.write_text(
                json.dumps(changed_case, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            next_snapshot = build_snapshot(repo)
            planned = plan_impact(snapshot, next_snapshot)
            next_pending = {
                "reasons": planned["reasons"],
                "corpus_cases": planned["corpus_cases"],
                "holdout_pairs": planned["holdout_pairs"],
                "review": True,
            }
            next_impact = plan_impact(
                snapshot,
                next_snapshot,
                pending=next_pending,
            )
            self.assertEqual(len(next_impact["corpus_cases"]), 1)
            self.assertEqual(next_impact["holdout_pairs"], [])
            next_ledger = {
                "schema_version": 1,
                "state": "refresh_required",
                "snapshot": next_snapshot,
                "prior_evidence": {
                    "source_commit": prior_commit,
                    "source_path": "evaluation/results/current.json",
                    "sha256": sha256_bytes(prior_encoded),
                },
                "pending": next_pending,
                "historical_cost": historical_cost_receipt(),
                "live_authority": None,
                "certification": None,
            }
            next_authority = complete_live_authority(
                next_ledger,
                next_snapshot,
                next_impact,
            )
            next_source_ledger = copy.deepcopy(next_ledger)
            next_source_ledger["live_authority"] = next_authority
            prior_path.write_text(
                json.dumps(
                    next_source_ledger,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            git("add", "evaluation/cases", "evaluation/results/current.json")
            git("commit", "-qm", "persist incremental authority")
            next_source_commit = git("rev-parse", "HEAD")
            next_source_tree = git("rev-parse", "HEAD^{tree}")

            engine_identity = engine_inventory(repo)
            changed_case_id = next_impact["corpus_cases"][0]
            partial_cases = [
                case_receipt(
                    changed_case_id,
                    next_snapshot["corpus"]["cases"][changed_case_id],
                    next_snapshot["package"],
                )
            ]
            partial_summary = {
                "schema_version": 1,
                "engine_generation": "0.4",
                "impact_token": next_authority["impact_token"],
                "live_authority_sha256": canonical_sha256(next_authority),
                "arm": "candidate",
                "model": settings["model"],
                "effort": settings["effort"],
                "timeout_seconds": settings["timeout_seconds"],
                "passed": 1,
                "total": 1,
                "uncached_input_tokens": 2,
                "telemetry_complete": True,
                "output_tokens": 1,
                "elapsed_seconds": 1.0,
                "cases": partial_cases,
            }
            next_evidence_sha = {
                "corpus_summary": write_evidence("corpus_summary", partial_summary),
                "offline_summary": write_evidence(
                    "offline_summary",
                    {
                        "schema_version": 1,
                        "engine_generation": "0.4",
                        "source_commit": next_source_commit,
                        "source_ledger_sha256": sha256_bytes(prior_path.read_bytes()),
                        "snapshot_sha256": canonical_sha256(next_snapshot),
                        "engine_manifest_sha256": next_snapshot["engine"][
                            "manifest_sha256"
                        ],
                        "gates": ["receipt"],
                        "receipt_artifact_sha256": next_snapshot["engine"][
                            "categories"
                        ]["artifact"],
                        "isolated_installation": None,
                    },
                ),
            }
            git("add", "evaluation/results/evidence")
            git("commit", "-qm", "incremental evidence")
            next_evidence_commit = git("rev-parse", "HEAD")
            next_locators = {
                name: {
                    "commit": next_evidence_commit,
                    "path": f"evaluation/results/evidence/{name}.json",
                    "git_blob": git(
                        "rev-parse",
                        f"{next_evidence_commit}:evaluation/results/evidence/{name}.json",
                    ),
                    "sha256": digest,
                }
                for name, digest in next_evidence_sha.items()
            }
            next_coverage = {
                "corpus": {
                    case_id: ("refreshed" if case_id == changed_case_id else "prior")
                    for case_id in next_snapshot["corpus"]["cases"]
                },
                "holdout": {
                    pair_id: "prior" for pair_id in next_snapshot["holdout"]["pairs"]
                },
            }
            next_certified = copy.deepcopy(next_ledger)
            next_certified["state"] = "certified"
            next_certified["pending"] = {
                "reasons": [],
                "corpus_cases": [],
                "holdout_pairs": [],
                "review": False,
            }
            next_certified["live_authority"] = next_authority
            next_certified["certification"] = {
                "schema_version": 1,
                "successor_source_commit": next_source_commit,
                "successor_source_tree": next_source_tree,
                "snapshot_sha256": canonical_sha256(next_snapshot),
                "engine_manifest_sha256": next_snapshot["engine"]["manifest_sha256"],
                "coverage": next_coverage,
                "evidence": next_locators,
                "live_authority_sha256": canonical_sha256(next_authority),
            }
            validate_ledger(next_certified, repo=repo)

            next_certified_encoded = (
                json.dumps(
                    next_certified,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n"
            ).encode()
            prior_path.write_bytes(next_certified_encoded)
            git("add", "evaluation/results/current.json")
            git("commit", "-qm", "persist incremental certification")
            artifact_prior_commit = git("rev-parse", "HEAD")

            artifact_module = repo / "evaluation" / "core" / "receipt.py"
            artifact_module.write_text(
                artifact_module.read_text(encoding="utf-8")
                + "\n# artifact-only serializer revision\n",
                encoding="utf-8",
            )
            artifact_snapshot = build_snapshot(repo)
            artifact_pending = {
                "reasons": ["artifact-only-refresh"],
                "corpus_cases": [],
                "holdout_pairs": [],
                "review": True,
            }
            artifact_impact = plan_impact(
                next_snapshot,
                artifact_snapshot,
                pending=artifact_pending,
            )
            self.assertEqual(
                artifact_impact["live_calls"], {"minimum": 0, "maximum": 0}
            )
            artifact_source_ledger = {
                "schema_version": 1,
                "state": "refresh_required",
                "snapshot": artifact_snapshot,
                "prior_evidence": {
                    "source_commit": artifact_prior_commit,
                    "source_path": "evaluation/results/current.json",
                    "sha256": sha256_bytes(next_certified_encoded),
                },
                "pending": artifact_pending,
                "historical_cost": historical_cost_receipt(),
                "live_authority": None,
                "certification": None,
            }
            prior_path.write_text(
                json.dumps(
                    artifact_source_ledger,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            git("add", "evaluation/core/receipt.py", "evaluation/results/current.json")
            git("commit", "-qm", "persist zero-live refresh source")
            artifact_source_commit = git("rev-parse", "HEAD")
            artifact_source_tree = git("rev-parse", "HEAD^{tree}")

            artifact_certified = copy.deepcopy(artifact_source_ledger)
            artifact_certified["state"] = "certified"
            artifact_certified["pending"] = {
                "reasons": [],
                "corpus_cases": [],
                "holdout_pairs": [],
                "review": False,
            }
            artifact_certified["certification"] = {
                "schema_version": 1,
                "successor_source_commit": artifact_source_commit,
                "successor_source_tree": artifact_source_tree,
                "snapshot_sha256": canonical_sha256(artifact_snapshot),
                "engine_manifest_sha256": artifact_snapshot["engine"][
                    "manifest_sha256"
                ],
                "coverage": {
                    "corpus": {
                        case_id: "prior"
                        for case_id in artifact_snapshot["corpus"]["cases"]
                    },
                    "holdout": {
                        pair_id: "prior"
                        for pair_id in artifact_snapshot["holdout"]["pairs"]
                    },
                },
                "evidence": {},
                "live_authority_sha256": canonical_sha256(None),
            }
            with self.assertRaisesRegex(ValueError, "offline"):
                validate_ledger(artifact_certified, repo=repo)

            offline_summary = {
                "schema_version": 1,
                "engine_generation": "0.4",
                "source_commit": artifact_source_commit,
                "source_ledger_sha256": sha256_bytes(prior_path.read_bytes()),
                "snapshot_sha256": canonical_sha256(artifact_snapshot),
                "engine_manifest_sha256": artifact_snapshot["engine"][
                    "manifest_sha256"
                ],
                "gates": ["receipt"],
                "receipt_artifact_sha256": artifact_snapshot["engine"]["categories"][
                    "artifact"
                ],
                "isolated_installation": None,
            }
            offline_sha = write_evidence("offline_summary", offline_summary)
            git("add", "evaluation/results/evidence/offline_summary.json")
            git("commit", "-qm", "offline artifact evidence")
            offline_commit = git("rev-parse", "HEAD")
            artifact_certified["certification"]["evidence"] = {
                "offline_summary": {
                    "commit": offline_commit,
                    "path": "evaluation/results/evidence/offline_summary.json",
                    "git_blob": git(
                        "rev-parse",
                        f"{offline_commit}:evaluation/results/evidence/offline_summary.json",
                    ),
                    "sha256": offline_sha,
                }
            }
            validate_ledger(artifact_certified, repo=repo)

            wrong_prior = copy.deepcopy(next_certified)
            wrong_prior["prior_evidence"]["sha256"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "prior certified ledger digest"):
                validate_ledger(wrong_prior, repo=repo)

    def test_verify_and_impact_commands_are_read_only_json(self) -> None:
        ledger_path = ROOT / "evaluation" / "results" / "current.json"
        ledger_bytes = ledger_path.read_bytes()
        ledger, current, expected_impact = live.load_state()
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
            if command == "verify":
                self.assertEqual(
                    payload,
                    {
                        "schema_version": 1,
                        "status": "ok",
                        "ledger_state": ledger["state"],
                        "ledger_sha256": ledger_sha256(ledger, repo=ROOT),
                        "snapshot_sha256": canonical_sha256(current),
                        "engine_manifest_sha256": engine_inventory(ROOT)[
                            "manifest_sha256"
                        ],
                        "pending_gates": expected_impact["gates"],
                        "live_authority_persisted": ledger["live_authority"]
                        is not None,
                    },
                )
                continue

            invocations = live.proposed_invocations(current, expected_impact)
            holdout_ready = not expected_impact["holdout_pairs"] or any(
                item["command"] == "holdout" for item in invocations
            )
            self.assertEqual(
                payload,
                {
                    **expected_impact,
                    "ledger_state": ledger["state"],
                    "snapshot_sha256": canonical_sha256(current),
                    "cost_approval_required": bool(
                        expected_impact["live_calls"]["maximum"]
                    ),
                    "live_authority_persisted": ledger["live_authority"] is not None,
                    "live_authority_ready": holdout_ready,
                    "proposed_invocations": invocations,
                    "impact_token": live.impact_token(ledger, current, expected_impact),
                },
            )

        self.assertEqual(ledger_path.read_bytes(), ledger_bytes)

        prior = copy.deepcopy(current)
        prior["package"]["artifact_sha256"] = (
            "0" * 64 if current["package"]["artifact_sha256"] != "0" * 64 else "f" * 64
        )
        incremental = plan_impact(
            prior,
            current,
            pending={
                "reasons": ["test-artifact-only-refresh"],
                "corpus_cases": [],
                "holdout_pairs": [],
                "review": True,
            },
        )
        self.assertEqual(incremental["gates"], ["isolated_install", "review"])
        self.assertEqual(incremental["live_calls"], {"minimum": 0, "maximum": 0})
        self.assertEqual(incremental["corpus_cases"], [])
        self.assertEqual(incremental["holdout_pairs"], [])

    def test_impact_token_cannot_self_authorize_a_live_command(self) -> None:
        ledger, current, impact = full_live_test_state()
        token = live.impact_token(ledger, current, impact)
        with tempfile.TemporaryDirectory() as raw:
            with (
                mock.patch.object(
                    live, "load_state", return_value=(ledger, current, impact)
                ),
                mock.patch.object(
                    live,
                    "require_authorized_invocation",
                    wraps=live.require_authorized_invocation,
                ) as authority_gate,
                mock.patch.object(live.corpus_engine, "run_authorized") as runner,
            ):
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
        authority_gate.assert_called_once()
        self.assertIsNone(authority_gate.call_args.args[0])
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
