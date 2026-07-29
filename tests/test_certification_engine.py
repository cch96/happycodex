from __future__ import annotations

import copy
import json
import multiprocessing
import os
from pathlib import Path
import pickle
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from evaluation import cli, live
from evaluation.core import ledger as ledger_engine
from evaluation.core.identity import (
    CORPUS_SEMANTIC_PATHS,
    IdentityError,
    canonical_sha256,
    engine_inventory,
    engine_paths_sha256,
    invocation_profile,
    package_identities,
)
from evaluation.core.impact import (
    CORPUS_MODEL_CALLS,
    build_snapshot,
    plan_impact,
)
from evaluation.core.ledger import ledger_sha256, validate_ledger
from evaluation.corpus import engine as corpus_engine
from evaluation.semantic import make_attempt_key, parse_facts, reduce_facts


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
    "evaluation/corpus/engine.py",
    "evaluation/holdout/__init__.py",
    "evaluation/holdout/blind.py",
    "evaluation/holdout/compare.py",
    "evaluation/holdout/engine.py",
    "evaluation/semantic/__init__.py",
    "evaluation/semantic/canonical.py",
    "evaluation/semantic/decide.py",
    "evaluation/semantic/parse.py",
    "evaluation/semantic/types.py",
}


def refreshed_coverage(snapshot: dict[str, object]) -> dict[str, object]:
    return {
        "corpus": {case_id: "refreshed" for case_id in snapshot["corpus"]["cases"]},
        "holdout": {pair_id: "refreshed" for pair_id in snapshot["holdout"]["pairs"]},
    }


def waived_coverage(snapshot: dict[str, object]) -> dict[str, object]:
    return {
        "corpus": {case_id: "waived" for case_id in snapshot["corpus"]["cases"]},
        "holdout": {pair_id: "waived" for pair_id in snapshot["holdout"]["pairs"]},
    }


def full_live_test_state() -> tuple[
    dict[str, object], dict[str, object], dict[str, object]
]:
    current = build_snapshot(ROOT)
    pending = {
        "gates": [
            "corpus",
            "executor_pilot",
            "holdout",
            "isolated_install",
            "receipt",
            "review",
        ],
        "corpus_cases": sorted(current["corpus"]["cases"]),
        "holdout_pairs": sorted(current["holdout"]["pairs"]),
    }
    ledger = {
        "schema_version": 1,
        "engine_generation": "0.6",
        "state": "refresh_required",
        "snapshot": current,
        "source_anchor": None,
        "pending": pending,
        "authorities": {"executor": None, "corpus": None, "holdout": None},
        "calibration_history": [],
        "accepted_evidence": [],
        "receipt_head": None,
        "certification": None,
    }
    impact = plan_impact(current, current, pending=pending)
    validate_ledger(ledger, repo=ROOT)
    return ledger, current, impact


def g013_authority_fixture() -> tuple[object, object, dict[str, str]]:
    from tests.test_semantic_core import adapter_authority, raw_envelope

    report = reduce_facts(parse_facts(raw_envelope()))
    authority = adapter_authority(report.facts.task, report.next_action)
    binding = {
        "task_id": report.facts.task.task.value,
        "root_task_id": report.facts.task.root_task.value,
        "executor_task_id": report.facts.task.executor_task.value,
        "owner_label": report.facts.task.owner.value,
        "destination_id": report.facts.task.destination.value,
        "lineage_digest": report.facts.task.lineage.value,
        "role_config_digest": report.facts.task.role_config.value,
        "repository_digest": report.facts.task.repository.value,
        "outcome_digest": report.facts.task.outcome.value,
        "message_id": authority.message_id.value,
        "turn_id": authority.turn_id.value,
        "content_digest": authority.content_digest.value,
        "session_id": "session-g013",
        "thread_id": "thread-g013",
        "permission_digest": "d" * 64,
        "claim_digest": "e" * 64,
    }
    return report, authority, binding


def g013_claim_worker(
    claim_root: str,
    key: str,
    start: object,
    results: object,
) -> None:
    start.wait()
    try:
        live._claim_file(
            Path(claim_root),
            key,
            {"schema_version": 1, "kind": "authority", "digest": "a" * 64},
        )
    except FileExistsError:
        results.put("collision")
    else:
        results.put("winner")


class CertificationIdentityTests(unittest.TestCase):
    def test_legacy_authority_construction_and_claim_apis_are_absent(self) -> None:
        for name in (
            "affirmative_approval_response",
            "validate_live_authority",
            "claim_authorized_invocation",
            "AuthorizedInvocation",
        ):
            self.assertFalse(hasattr(ledger_engine, name), name)

    def test_legacy_ledger_names_are_absent_from_production(self) -> None:
        production = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "evaluation/cli.py",
                "evaluation/live.py",
                "evaluation/core/ledger.py",
                "evaluation/core/impact.py",
                "evaluation/core/receipt.py",
                "evaluation/corpus/engine.py",
                "evaluation/holdout/engine.py",
            )
        )
        for legacy in ("live_authority", "live_attempts", "historical_cost"):
            self.assertNotIn(legacy, production)
        self.assertNotIn("current-task/user", production)

    def test_legacy_source_and_certification_readers_are_absent(self) -> None:
        for name in (
            "_validate_source_identity",
            "_load_evidence",
            "_validate_certification_receipt",
        ):
            self.assertFalse(hasattr(ledger_engine, name), name)

    def test_active_ledger_is_exact_fresh_generation_6_genesis(self) -> None:
        active = json.loads(
            (ROOT / "evaluation" / "results" / "current.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            set(active),
            {
                "schema_version",
                "engine_generation",
                "state",
                "snapshot",
                "source_anchor",
                "pending",
                "authorities",
                "calibration_history",
                "accepted_evidence",
                "receipt_head",
                "certification",
            },
        )
        self.assertEqual(active["schema_version"], 1)
        self.assertEqual(active["engine_generation"], "0.6")
        self.assertEqual(active["state"], "refresh_required")
        self.assertIsNone(active["source_anchor"])
        self.assertEqual(
            active["pending"]["gates"],
            [
                "corpus",
                "executor_pilot",
                "holdout",
                "isolated_install",
                "receipt",
                "review",
            ],
        )
        self.assertEqual(
            active["pending"]["corpus_cases"],
            sorted(active["snapshot"]["corpus"]["cases"]),
        )
        self.assertEqual(
            active["pending"]["holdout_pairs"],
            sorted(active["snapshot"]["holdout"]["pairs"]),
        )
        self.assertEqual(
            active["authorities"],
            {"executor": None, "corpus": None, "holdout": None},
        )
        self.assertEqual(active["calibration_history"], [])
        self.assertEqual(active["accepted_evidence"], [])
        self.assertIsNone(active["receipt_head"])
        self.assertIsNone(active["certification"])
        for legacy in ("historical_cost", "live_attempts", "live_authority"):
            self.assertNotIn(legacy, active)
        validate_ledger(active, repo=ROOT)

    def test_active_generation_rejects_legacy_envelopes_and_evidence(self) -> None:
        active = json.loads(
            (ROOT / "evaluation" / "results" / "current.json").read_text(
                encoding="utf-8"
            )
        )
        for generation in ("0.4", "0.5"):
            invalid = copy.deepcopy(active)
            invalid["engine_generation"] = generation
            with self.assertRaisesRegex(ValueError, "generation|envelope"):
                validate_ledger(invalid, repo=ROOT)
        for legacy, value in (
            ("historical_cost", {}),
            ("live_attempts", {}),
            ("live_authority", None),
        ):
            invalid = copy.deepcopy(active)
            invalid[legacy] = value
            with self.assertRaisesRegex(ValueError, "envelope"):
                validate_ledger(invalid, repo=ROOT)
        self.assertEqual(active["accepted_evidence"], [])
        self.assertFalse(
            any(
                "evaluation/results/evidence" in json.dumps(value)
                for value in active.values()
            )
        )

    def test_active_producers_and_validators_are_generation_6_only(self) -> None:
        receipt = (ROOT / "evaluation/core/receipt.py").read_text(encoding="utf-8")
        self.assertNotIn('"engine_generation": "0.4"', receipt)
        self.assertIn('"engine_generation": "0.6"', receipt)
        for relative in (
            "evaluation/corpus/engine.py",
            "evaluation/holdout/engine.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn('"engine_generation": "0.4"', source)
            self.assertIn("unavailable until Batch3", source)
        validator = (ROOT / "evaluation/core/ledger.py").read_text(encoding="utf-8")
        self.assertNotIn('engine_generation") != "0.4"', validator)
        self.assertIn('engine_generation") != "0.6"', validator)

    def test_generation_6_has_no_prior_cost_or_attempt_surface(self) -> None:
        impact_source = (ROOT / "evaluation/core/impact.py").read_text(
            encoding="utf-8"
        )
        live_source = (ROOT / "evaluation/live.py").read_text(encoding="utf-8")
        self.assertNotIn("historical_cost_receipt", impact_source)
        self.assertNotIn('ledger["live_attempts"]', live_source)

    def test_generation_6_verify_is_green_refresh_required(self) -> None:
        with mock.patch("builtins.print") as output:
            self.assertEqual(cli.verify_command(), 0)
        payload = json.loads(output.call_args.args[0])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["ledger_state"], "refresh_required")
        self.assertFalse(payload["certified"])
        self.assertEqual(
            payload["pending_gates"],
            [
                "corpus",
                "executor_pilot",
                "holdout",
                "isolated_install",
                "receipt",
                "review",
            ],
        )

    def test_four_terminal_commands_are_read_only_and_zero_effect(self) -> None:
        ledger_path = ROOT / "evaluation" / "results" / "current.json"
        ledger_before = ledger_path.read_bytes()
        status_before = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        commands = (
            ("verify",),
            ("executor", "--dry-run"),
            ("corpus", "--dry-run"),
            ("holdout", "--dry-run"),
        )
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, "-m", "evaluation.cli", *command],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                payload = json.loads(completed.stdout)
                if command == ("verify",):
                    self.assertEqual(payload["ledger_state"], "refresh_required")
                    self.assertFalse(payload["certified"])
                elif command == ("executor", "--dry-run"):
                    self.assertTrue(payload["dry_run"])
                    self.assertTrue(all(value == 0 for value in payload["effects"].values()))
        self.assertEqual(ledger_path.read_bytes(), ledger_before)
        status_after = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertEqual(status_after, status_before)

    def test_current_json_bytes_do_not_contribute_to_build_snapshot(self) -> None:
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
            before = build_snapshot(clone)
            (clone / "evaluation" / "results" / "current.json").write_text(
                '{"deliberately":"different"}\n', encoding="utf-8"
            )
            self.assertEqual(build_snapshot(clone), before)

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
        self.assertEqual(len(snapshot["corpus"]["cases"]), 17)
        self.assertEqual(len(snapshot["holdout"]["pairs"]), 3)
        self.assertEqual(
            snapshot["package"]["artifact_sha256"],
            package_identities(ROOT)["artifact_sha256"],
        )
        self.assertEqual(
            set(snapshot["settings"]["toolchain"]), {"python", "codex", "git", "rg"}
        )
        python = snapshot["settings"]["toolchain"]["python"]
        self.assertEqual(set(python), {"path", "sha256", "version"})
        self.assertRegex(python["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            snapshot["engine"]["manifest_sha256"],
            engine_inventory(ROOT)["manifest_sha256"],
        )

    def test_no_change_has_no_gate_or_live_call(self) -> None:
        impact = plan_impact(self.snapshot, self.snapshot)
        self.assertEqual(impact["gates"], [])
        self.assertIsNone(impact["live_calls"])
        self.assertIsNone(impact["cost"])
        self.assertEqual(impact["reasons"], [])

    def test_one_case_change_invalidates_only_that_corpus_case(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        case_id = sorted(changed["corpus"]["cases"])[0]
        changed["corpus"]["cases"][case_id] = "f" * 64

        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["corpus_cases"], [case_id])
        self.assertEqual(impact["holdout_pairs"], [])
        self.assertEqual(impact["gates"], ["corpus"])
        self.assertIsNone(impact["live_calls"])
        self.assertIsNone(impact["cost"])

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
                "gates": ["corpus"],
                "corpus_cases": ["pre-freeze-compaction"],
                "holdout_pairs": [],
            },
        )
        self.assertIsNone(impact["live_calls"])

    def test_removed_case_blocks_impact_instead_of_reporting_zero_cost(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["corpus"]["cases"].pop(sorted(changed["corpus"]["cases"])[0])

        with self.assertRaisesRegex(IdentityError, "removed corpus case"):
            plan_impact(self.snapshot, changed)

    def test_corpus_semantic_bundle_has_one_authoritative_exact_path_set(self) -> None:
        from evaluation.core import impact as impact_engine

        self.assertIs(corpus_engine.CORPUS_SEMANTIC_PATHS, CORPUS_SEMANTIC_PATHS)
        self.assertIs(impact_engine.CORPUS_SEMANTIC_PATHS, CORPUS_SEMANTIC_PATHS)
        self.assertEqual(len(CORPUS_SEMANTIC_PATHS), 6)
        inventory = engine_inventory(ROOT)
        expected = {
            item["path"]
            for item in inventory["entries"]
            if item["path"] in CORPUS_SEMANTIC_PATHS
        }
        self.assertEqual(expected, set(CORPUS_SEMANTIC_PATHS))
        with self.assertRaisesRegex(IdentityError, "source bundle"):
            engine_paths_sha256(
                inventory,
                set(CORPUS_SEMANTIC_PATHS) | {"evaluation/corpus/contract.py"},
            )

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
                else:
                    changed["engine"]["scopes"]["corpus_semantic"] = "d" * 64
                impact = plan_impact(self.snapshot, changed)
                self.assertEqual(len(impact["corpus_cases"]), 17)
                self.assertEqual(len(impact["holdout_pairs"]), 3)
                self.assertEqual(impact["gates"], ["corpus", "holdout"])
                self.assertIsNone(impact["live_calls"])

    def test_holdout_only_harness_change_does_not_rerun_corpus(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["harness"] = "e" * 64
        changed["engine"]["scopes"]["holdout_harness"] = "d" * 64

        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["corpus_cases"], [])
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertEqual(impact["gates"], ["holdout"])
        self.assertIsNone(impact["live_calls"])

    def test_holdout_policy_change_does_not_rerun_corpus(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["semantic"] = "e" * 64
        changed["engine"]["scopes"]["holdout_semantic"] = "d" * 64

        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["corpus_cases"], [])
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertEqual(impact["gates"], ["holdout"])
        self.assertIsNone(impact["live_calls"])

    def test_partial_pending_holdout_expands_to_the_executable_adaptive_scope(
        self,
    ) -> None:
        pair_id = sorted(self.snapshot["holdout"]["pairs"])[0]
        impact = plan_impact(
            self.snapshot,
            self.snapshot,
            pending={
                "gates": ["holdout"],
                "corpus_cases": [],
                "holdout_pairs": [pair_id],
            },
        )
        self.assertEqual(
            impact["holdout_pairs"], sorted(self.snapshot["holdout"]["pairs"])
        )
        self.assertIsNone(impact["live_calls"])

    def test_artifact_engine_or_package_change_needs_no_model_call(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["engine"]["categories"]["artifact"] = "d" * 64
        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["gates"], ["receipt"])
        self.assertIsNone(impact["live_calls"])

    def test_real_control_mutations_fail_closed_but_sanitizer_is_artifact(self) -> None:
        for relative, expected_calls in (
            ("evaluation/cli.py", {"minimum": 23, "maximum": 25}),
            ("evaluation/core/impact.py", {"minimum": 23, "maximum": 25}),
            ("evaluation/core/ledger.py", {"minimum": 23, "maximum": 25}),
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
                self.assertIsNone(impact["live_calls"])
                if relative.endswith("receipt.py"):
                    self.assertEqual(impact["gates"], ["receipt"])
                else:
                    self.assertEqual(impact["gates"][:2], ["corpus", "holdout"])

        changed = copy.deepcopy(self.snapshot)
        changed["package"]["artifact_sha256"] = "c" * 64
        impact = plan_impact(self.snapshot, changed)
        self.assertEqual(impact["gates"], ["isolated_install"])
        self.assertIsNone(impact["live_calls"])

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

    def test_refresh_ledger_has_no_prior_cost_attempt_or_evidence(self) -> None:
        ledger, current, impact = full_live_test_state()
        self.assertEqual(current, self.snapshot)
        self.assertEqual(len(impact["corpus_cases"]), 17)
        self.assertEqual(len(impact["holdout_pairs"]), 3)
        self.assertIsNone(impact["live_calls"])
        self.assertIsNone(impact["cost"])

        invalid = copy.deepcopy(ledger)
        invalid["historical_cost"] = {}
        with self.assertRaisesRegex(ValueError, "envelope"):
            validate_ledger(invalid, repo=ROOT)
        self.assertEqual(ledger["calibration_history"], [])
        self.assertEqual(ledger["accepted_evidence"], [])
        self.assertEqual(
            ledger["authorities"],
            {"executor": None, "corpus": None, "holdout": None},
        )


class CertificationReceiptAndCliTests(unittest.TestCase):
    def test_executor_dry_run_is_deterministic_and_zero_effect(self) -> None:
        with (
            mock.patch("subprocess.run", side_effect=AssertionError("subprocess")),
            mock.patch.object(
                corpus_engine,
                "build_fixture",
                side_effect=AssertionError("fixture"),
            ),
            mock.patch("builtins.print") as output,
        ):
            self.assertEqual(cli.main(["executor", "--dry-run"]), 0)
        payload = json.loads(output.call_args.args[0])
        self.assertEqual(
            payload,
            {
                "schema_generation": 6,
                "command": "executor",
                "dry_run": True,
                "invocation_profile": invocation_profile(
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout_seconds=300,
                    arm="candidate",
                    session_mode="fresh",
                ),
                "effects": {
                    "capabilities_minted": 0,
                    "attempts_claimed": 0,
                    "authorities_consumed": 0,
                    "fixtures_created": 0,
                    "outputs_created": 0,
                    "workspaces_created": 0,
                    "subprocesses": 0,
                    "model_calls": 0,
                    "network_calls": 0,
                },
                "gate_authority_required": True,
            },
        )

    def test_terminal_events_bind_one_result_usage_completion_and_eof(self) -> None:
        final = {"decision": "continue", "value": "bound"}
        binding = {
            "provider": "openai",
            "session_id": "session-1",
            "thread_id": "thread-1",
            "action_id": "evaluate:case-1",
            "attempt_key": "a" * 64,
        }
        profile = invocation_profile(
            model="gpt-5.6-sol",
            effort="high",
            timeout_seconds=300,
            arm="candidate",
        )
        events = [
            {
                "type": "thread.started",
                "thread_id": binding["thread_id"],
            },
            {"type": "turn.started"},
            {
                "type": "item.started",
                "item": {
                    "aggregated_output": "",
                    "command": "rg --files",
                    "exit_code": None,
                    "id": "tool-1",
                    "status": "in_progress",
                    "type": "command_execution",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "tool-1",
                    "type": "command_execution",
                    "aggregated_output": "bounded fixture",
                    "command": "rg --files",
                    "exit_code": 0,
                    "status": "completed",
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "result-1",
                    "type": "agent_message",
                    "text": json.dumps(final),
                },
            },
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 10,
                    "cached_input_tokens": 2,
                    "cache_write_input_tokens": 1,
                    "output_tokens": 3,
                    "reasoning_output_tokens": 1,
                },
            },
        ]

        parsed, usage, thread_id, terminal = corpus_engine.parse_events(
            "\n".join(json.dumps(item) for item in events),
            binding=binding,
            invocation_profile=profile,
        )
        self.assertEqual(parsed, final)
        self.assertEqual(usage["output_tokens"], 3)
        self.assertEqual(thread_id, "thread-1")
        self.assertEqual(terminal["provider"], binding["provider"])
        self.assertEqual(terminal["session_id"], binding["session_id"])
        self.assertEqual(terminal["action_id"], binding["action_id"])
        self.assertEqual(terminal["attempt_key"], binding["attempt_key"])
        self.assertEqual(terminal["thread_id"], binding["thread_id"])
        self.assertEqual(terminal["result_id"], "result-1")
        self.assertEqual(terminal["result_sha256"], canonical_sha256(final))
        self.assertEqual(terminal["provenance"], "validated_invocation+native_stream")
        self.assertEqual(terminal["terminal_ordinal"], 4)
        self.assertRegex(terminal["turn_id"], r"^[0-9a-f]{64}$")
        self.assertRegex(terminal["stream_sha256"], r"^[0-9a-f]{64}$")

        variants = {
            "duplicate result": [*events[:-1], events[-2], events[-1]],
            "duplicate completion": [*events, events[-1]],
            "late result": [*events, events[-2]],
            "extra terminal": [
                *events,
                {"type": "terminal.extra", "value": "forbidden"},
            ],
            "unpaired prefix": [
                *events[:2],
                {
                    "type": "item.completed",
                    "item": {
                        "aggregated_output": "",
                        "command": "rg",
                        "exit_code": 0,
                        "id": "tool-2",
                        "status": "completed",
                        "type": "command_execution",
                    },
                },
                *events[-2:],
            ],
            "unknown terminal shape": [
                *events[:-2],
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": json.dumps(final)},
                },
                events[-1],
            ],
        }
        for label, variant in variants.items():
            with self.subTest(label=label), self.assertRaisesRegex(
                ValueError, "terminal|event|digest|EOF"
            ):
                corpus_engine.parse_events(
                    "\n".join(json.dumps(item) for item in variant),
                    binding=binding,
                    invocation_profile=profile,
                )

        collab_profile = invocation_profile(
            model="gpt-5.6-sol",
            effort="high",
            timeout_seconds=300,
            arm="candidate",
            allowed_tools=("collaboration",),
        )
        collab_base = {
            "agents_states": {},
            "id": "collab-1",
            "prompt": None,
            "receiver_thread_ids": ["thread-child"],
            "sender_thread_id": "thread-1",
            "tool": "wait",
            "type": "collab_tool_call",
        }
        collab_events = [
            events[0],
            events[1],
            {
                "type": "item.started",
                "item": {**collab_base, "status": "in_progress"},
            },
            {
                "type": "item.completed",
                "item": {**collab_base, "status": "completed"},
            },
            events[-2],
            events[-1],
        ]
        corpus_engine.parse_events(
            "\n".join(json.dumps(item) for item in collab_events),
            binding=binding,
            invocation_profile=collab_profile,
        )
        with self.assertRaisesRegex(ValueError, "invocation profile"):
            corpus_engine.parse_events(
                "\n".join(json.dumps(item) for item in collab_events),
                binding=binding,
                invocation_profile=profile,
            )

    def test_041_is_fresh_only_with_no_prior_evidence_surface(self) -> None:
        current = json.loads(
            (ROOT / "evaluation" / "results" / "current.json").read_text(
                encoding="utf-8"
            )
        )
        source = (ROOT / "evaluation" / "core" / "ledger.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("prior_evidence", ledger_engine.LEDGER_FIELDS)
        self.assertNotIn("prior_evidence", current)
        self.assertNotIn("_load_prior_certified_ledger", source)
        self.assertNotIn('disposition == "prior"', source)
        self.assertNotIn('"prior"', source)

    def test_corpus_cases_run_with_a_four_worker_bound_and_stable_order(self) -> None:
        case_ids = [f"case-{index}" for index in range(8)]
        barrier = threading.Barrier(corpus_engine.CORPUS_MAX_WORKERS)
        lock = threading.Lock()
        active = 0
        maximum_active = 0

        def evaluate(case_id: str) -> dict[str, object]:
            nonlocal active, maximum_active
            with lock:
                active += 1
                maximum_active = max(maximum_active, active)
            barrier.wait(timeout=2)
            with lock:
                active -= 1
            return {"case": case_id}

        results = corpus_engine._evaluate_cases_bounded(case_ids, evaluate)

        self.assertEqual(
            [result["case"] for result in results],
            case_ids,
        )
        self.assertEqual(maximum_active, corpus_engine.CORPUS_MAX_WORKERS)
        self.assertEqual(corpus_engine.CORPUS_MAX_WORKERS, 4)

    def test_corpus_worker_failure_propagates_without_retry(self) -> None:
        attempts: dict[str, int] = {}

        def evaluate(case_id: str) -> dict[str, object]:
            attempts[case_id] = attempts.get(case_id, 0) + 1
            raise RuntimeError(f"infra failure: {case_id}")

        with self.assertRaisesRegex(RuntimeError, "infra failure"):
            corpus_engine._evaluate_cases_bounded(
                [f"case-{index}" for index in range(8)], evaluate
            )

        self.assertTrue(attempts)
        self.assertLessEqual(
            set(attempts),
            {f"case-{index}" for index in range(corpus_engine.CORPUS_MAX_WORKERS)},
        )
        self.assertEqual(set(attempts.values()), {1})

    def test_corpus_frontier_stops_after_replacement_failure(self) -> None:
        barrier = threading.Barrier(corpus_engine.CORPUS_MAX_WORKERS)
        failure_started = threading.Event()
        seen: list[int] = []
        lock = threading.Lock()

        def evaluate(case_id: str) -> dict[str, object]:
            index = int(case_id.removeprefix("case-"))
            with lock:
                seen.append(index)
            if index < corpus_engine.CORPUS_MAX_WORKERS:
                barrier.wait(timeout=2)
            elif index == corpus_engine.CORPUS_MAX_WORKERS:
                failure_started.set()
                raise RuntimeError("replacement failed")
            else:
                failure_started.wait(timeout=2)
                time.sleep(0.02)
            return {"case": case_id}

        with self.assertRaisesRegex(RuntimeError, "replacement failed"):
            corpus_engine._evaluate_cases_bounded(
                [f"case-{index}" for index in range(12)], evaluate
            )

        self.assertLessEqual(
            set(seen),
            {f for f in range(corpus_engine.CORPUS_MAX_WORKERS * 2)},
        )
        self.assertNotIn(corpus_engine.CORPUS_MAX_WORKERS * 2, seen)

    def test_timeout_and_nonzero_exit_are_infrastructure_failures(self) -> None:
        for label, completed, timed_out in (
            (
                "timeout",
                subprocess.CompletedProcess(["codex"], 124, "", "timeout"),
                True,
            ),
            (
                "nonzero",
                subprocess.CompletedProcess(["codex"], 7, "partial", "failed"),
                False,
            ),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as raw:
                output = Path(raw)
                corpus_engine._persist_phase_raw(output, label, completed)
                with self.assertRaises(corpus_engine.InfrastructureFailure):
                    corpus_engine._require_model_phase_success(
                        completed,
                        timed_out=timed_out,
                        phase=label,
                    )
                self.assertEqual(
                    (output / f"{label}-events.jsonl").read_text(), completed.stdout
                )
                self.assertEqual(
                    (output / f"{label}-stderr.txt").read_text(), completed.stderr
                )

    def test_native_review_remains_an_external_completion_gate(self) -> None:
        self.assertIn("review", ledger_engine.PENDING_GATES)
        self.assertFalse(hasattr(ledger_engine, "COVERAGE_FIELDS"))
        self.assertFalse(hasattr(ledger_engine, "_validate_review_receipt"))

    def test_refresh_required_cannot_carry_a_certification(self) -> None:
        ledger, _current, _impact = full_live_test_state()
        self.assertEqual(ledger["state"], "refresh_required")
        self.assertIsNone(ledger["certification"])
        self.assertEqual(
            ledger["authorities"],
            {"executor": None, "corpus": None, "holdout": None},
        )
        validate_ledger(ledger)

        invalid = copy.deepcopy(ledger)
        invalid["state"] = "certified"
        invalid["certification"] = {}
        with self.assertRaisesRegex(ValueError, "certification ledger"):
            validate_ledger(invalid)

    def test_live_dispatch_refuses_before_authority_or_runner_effect(self) -> None:
        ledger, current, impact = full_live_test_state()
        with (
            mock.patch.object(
                live,
                "load_state",
                side_effect=AssertionError("state load reached"),
            ) as state,
            mock.patch.object(corpus_engine, "run_authorized") as runner,
            self.assertRaisesRegex(SystemExit, "2"),
        ):
            cli.main(
                [
                    "corpus",
                    "--bind-impact",
                    live.impact_token(current, impact),
                    "--output",
                    "/tmp/happycodex-binding-test",
                ]
            )
        state.assert_not_called()
        runner.assert_not_called()

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

    def test_verify_preserves_repo_context_for_certified_ledger_hash(self) -> None:
        ledger = {
            "state": "refresh_required",
            "authorities": {"executor": None, "corpus": None, "holdout": None},
        }
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

    def test_certified_state_requires_a_digest_bound_successor_receipt(self) -> None:
        ledger, current, impact = full_live_test_state()
        del current, impact
        certified = copy.deepcopy(ledger)
        certified["state"] = "certified"
        certified["certification"] = {
            "forbidden_before_generation_6_evidence_work": True
        }
        with self.assertRaisesRegex(ValueError, "certification ledger"):
            validate_ledger(certified, repo=ROOT)

    def test_verify_and_impact_commands_are_read_only_json(self) -> None:
        ledger_path = ROOT / "evaluation" / "results" / "current.json"
        ledger_bytes = ledger_path.read_bytes()
        ledger, current, expected_impact = live.load_state()
        verify = subprocess.run(
            [sys.executable, "-m", "evaluation.cli", "verify"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)
        payload = json.loads(verify.stdout)
        self.assertEqual(payload["ledger_state"], "refresh_required")
        self.assertFalse(payload["certified"])
        self.assertEqual(payload["pending_gates"], expected_impact["gates"])
        self.assertEqual(payload["ledger_sha256"], ledger_sha256(ledger, repo=ROOT))
        self.assertEqual(payload["snapshot_sha256"], canonical_sha256(current))
        impact = subprocess.run(
            [sys.executable, "-m", "evaluation.cli", "impact"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(impact.returncode, 0)
        self.assertIn("cost envelope", impact.stderr)
        self.assertEqual(ledger_path.read_bytes(), ledger_bytes)

    def test_impact_token_cannot_self_authorize_a_live_command(self) -> None:
        ledger, current, impact = full_live_test_state()
        token = live.impact_token(current, impact)
        with tempfile.TemporaryDirectory() as raw:
            with (
                mock.patch.object(
                    live,
                    "load_state",
                    side_effect=AssertionError("state load reached"),
                ) as state,
                mock.patch.object(corpus_engine, "run_authorized") as runner,
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
        state.assert_not_called()
        runner.assert_not_called()

    def test_missing_generation_6_authority_refuses_before_snapshot_subprocess(self) -> None:
        ledger, current, impact = full_live_test_state()
        with (
            mock.patch.object(
                live,
                "load_state",
                side_effect=AssertionError("snapshot subprocess boundary reached"),
            ) as state,
            mock.patch.object(corpus_engine, "build_fixture") as fixture,
            self.assertRaisesRegex(SystemExit, "2"),
        ):
            cli.main(
                [
                    "corpus",
                    "--output",
                    "/tmp/happycodex-preflight-order-test",
                    "--bind-impact",
                    live.impact_token(current, impact),
                ]
            )
        state.assert_not_called()
        fixture.assert_not_called()


class G013SourceContractTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _claim_root(self, repo: Path) -> Path:
        raw = Path(self._git(repo, "rev-parse", "--git-common-dir"))
        common = raw if raw.is_absolute() else repo / raw
        root = common.resolve() / "happycodex" / "effect-claims" / "v6"
        root.mkdir(parents=True)
        root.chmod(0o700)
        return root

    def _capability(self) -> tuple[object, object, dict[str, str]]:
        report, authority, binding = g013_authority_fixture()
        issue = getattr(live, "_issue_trusted_host_context")
        context = issue(authority, binding)
        with mock.patch.object(live, "_trusted_host_context", return_value=context):
            capability = live._authorize_effect(report, object())
        return capability, report, binding

    def test_g013_source_anchor_is_null_preanchor_and_archive_bound(self) -> None:
        from evaluation.core import identity as identity_engine

        active = json.loads(
            (ROOT / "evaluation" / "results" / "current.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("source_anchor", active)
        self.assertIsNone(active["source_anchor"])
        validate_ledger(active, repo=ROOT)

        invalid = copy.deepcopy(active)
        invalid["source_anchor"] = {}
        with self.assertRaisesRegex(ValueError, "source anchor"):
            validate_ledger(invalid, repo=ROOT)

        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "source"
            repo.mkdir()
            for relative in (".agents", ".codex-plugin", "skills", "evaluation"):
                shutil.copytree(ROOT / relative, repo / relative)
            shutil.copy2(ROOT / "README.md", repo / "README.md")
            self._git(repo, "init")
            self._git(repo, "config", "user.name", "G013 Test")
            self._git(repo, "config", "user.email", "g013@example.invalid")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-m", "fixture: source archive")
            identity = identity_engine.source_archive_identity(repo, "HEAD")
            self.assertEqual(identity["source_commit"], self._git(repo, "rev-parse", "HEAD"))
            self.assertEqual(
                identity["source_tree"], self._git(repo, "rev-parse", "HEAD^{tree}")
            )
            self.assertEqual(identity["package"], package_identities(repo))
            self.assertEqual(
                identity["engine_manifest_sha256"],
                engine_inventory(repo)["manifest_sha256"],
            )
            self.assertEqual(
                identity["executor_role_sha256"],
                identity_engine.executor_role_identity(repo),
            )
            (repo / "README.md").write_text("uncommitted drift\n", encoding="utf-8")
            self.assertEqual(
                identity_engine.source_archive_identity(repo, "HEAD"),
                identity,
            )

    def test_g013_private_host_context_is_the_only_positive_authority_path(
        self,
    ) -> None:
        report, authority, binding = g013_authority_fixture()
        with (
            mock.patch.dict(
                os.environ,
                {
                    "HAPPYCODEX_AUTHORITY": json.dumps(binding),
                    "HAPPYCODEX_APPROVED": "yes",
                },
            ),
            self.assertRaisesRegex(ValueError, "trusted host"),
        ):
            live._authorize_effect(report, {"authority": binding, "approved": True})

        issue = getattr(live, "_issue_trusted_host_context")
        context = issue(authority, binding)
        with mock.patch.object(live, "_trusted_host_context", return_value=context):
            capability = live._authorize_effect(report, object())
        self.assertIs(live._rebind_capability(capability, binding), capability)
        self.assertFalse(hasattr(live, "issue_authority"))
        self.assertFalse(hasattr(live, "test_authority_factory"))

        with self.assertRaises(TypeError):
            copy.copy(capability)
        with self.assertRaises(TypeError):
            pickle.dumps(capability)
        for field in binding:
            changed = dict(binding)
            changed[field] = (
                "f" * 64 if field.endswith("_digest") else f"wrong-{field}"
            )
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "capability"
            ):
                live._rebind_capability(capability, changed)
        with (
            mock.patch.object(live.os, "getpid", return_value=os.getpid() + 1),
            self.assertRaisesRegex(ValueError, "process"),
        ):
            live._rebind_capability(capability, binding)

    def test_g013_claim_order_is_exact_and_faults_precede_effects(self) -> None:
        capability, report, _binding = self._capability()
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            root = self._claim_root(repo)
            request_type = getattr(live, "_ClaimRequest")
            request = request_type(
                repo=repo,
                authority_digest="a" * 64,
                attempt_key=make_attempt_key(report),
                resource_digests=("c" * 64, "b" * 64),
                output_digest="d" * 64,
            )
            order: list[str] = []
            real_rebind = live._rebind_capability

            def claim(_root: Path, key: str, _payload: dict[str, object]) -> None:
                self.assertEqual(_root, root)
                order.append(key.split("-", 1)[0])

            def rebind(item: object, binding: dict[str, str] | None = None) -> object:
                order.append("rebind")
                return real_rebind(item, binding)

            with (
                mock.patch.object(live, "_claim_file", side_effect=claim),
                mock.patch.object(live, "_rebind_capability", side_effect=rebind),
            ):
                live._consume_effect_claims(
                    capability,
                    request,
                    lambda: order.append("effects"),
                )
                live._run_model_phase(
                    capability,
                    "e" * 64,
                    lambda: order.append("model"),
                )
            self.assertEqual(
                order,
                [
                    "rebind",
                    "authority",
                    "attempt",
                    "resource",
                    "resource",
                    "output",
                    "rebind",
                    "effects",
                    "rebind",
                    "phase",
                    "rebind",
                    "model",
                ],
            )

        for fail_after in range(1, 6):
            with self.subTest(fail_after=fail_after), tempfile.TemporaryDirectory() as raw:
                repo = Path(raw) / "repo"
                repo.mkdir()
                self._git(repo, "init")
                root = self._claim_root(repo)
                request = live._ClaimRequest(
                    repo=repo,
                    authority_digest="a" * 64,
                    attempt_key=make_attempt_key(report),
                    resource_digests=("b" * 64, "c" * 64),
                    output_digest="d" * 64,
                )
                real_claim = live._claim_file
                count = 0

                def fault(
                    claim_root: Path,
                    key: str,
                    payload: dict[str, object],
                ) -> None:
                    nonlocal count
                    real_claim(claim_root, key, payload)
                    count += 1
                    if count == fail_after:
                        raise RuntimeError("injected claim failure")

                effect = mock.Mock()
                with (
                    mock.patch.object(live, "_claim_file", side_effect=fault),
                    self.assertRaisesRegex(RuntimeError, "injected"),
                ):
                    live._consume_effect_claims(capability, request, effect)
                effect.assert_not_called()
                self.assertEqual(len(list(root.iterdir())), fail_after)

    def test_g013_phase_claim_collision_prevents_model_invocation(self) -> None:
        capability, report, _binding = self._capability()
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            root = self._claim_root(repo)
            request = live._ClaimRequest(
                repo=repo,
                authority_digest="a" * 64,
                attempt_key=make_attempt_key(report),
                resource_digests=("b" * 64,),
                output_digest="d" * 64,
            )
            live._consume_effect_claims(capability, request, lambda: None)
            live._claim_file(
                root,
                "phase-" + "e" * 64,
                {"schema_version": 1, "kind": "phase", "digest": "e" * 64},
            )
            invoke = mock.Mock()
            with self.assertRaises(FileExistsError):
                live._run_model_phase(capability, "e" * 64, invoke)
            invoke.assert_not_called()

    def test_g013_claim_race_modes_and_output_paths_are_pre_effect(self) -> None:
        from evaluation.holdout import engine as holdout_engine

        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            root = self._claim_root(repo)
            context = multiprocessing.get_context("fork")
            start = context.Event()
            results = context.Queue()
            workers = [
                context.Process(
                    target=g013_claim_worker,
                    args=(str(root), "authority-" + "a" * 64, start, results),
                )
                for _index in range(2)
            ]
            for worker in workers:
                worker.start()
            start.set()
            outcomes = sorted(results.get(timeout=5) for _worker in workers)
            for worker in workers:
                worker.join(timeout=5)
                self.assertEqual(worker.exitcode, 0)
            self.assertEqual(outcomes, ["collision", "winner"])
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            claimed = next(root.iterdir())
            self.assertEqual(claimed.stat().st_mode & 0o777, 0o600)

            safe_parent = Path(raw) / "outputs"
            safe_parent.mkdir()
            corpus_output = safe_parent / "corpus"
            holdout_output = safe_parent / "holdout"
            self.assertEqual(
                corpus_engine.resolve_output_path(corpus_output, plugin=ROOT),
                corpus_output.resolve(),
            )
            self.assertFalse(corpus_output.exists())
            self.assertEqual(
                holdout_engine.resolve_output(holdout_output, ROOT),
                holdout_output.resolve(),
            )
            self.assertFalse(holdout_output.exists())
            for resolver in (
                lambda: corpus_engine.resolve_output_path(None, plugin=ROOT),
                lambda: holdout_engine.resolve_output(None, ROOT),
                lambda: corpus_engine.resolve_output_path(
                    safe_parent / "missing" / "output",
                    plugin=ROOT,
                ),
            ):
                with self.assertRaisesRegex(ValueError, "explicit|parent"):
                    resolver()
            symlink = safe_parent / "symlink"
            symlink.symlink_to(safe_parent / "target")
            for resolver in (
                lambda: corpus_engine.resolve_output_path(symlink, plugin=ROOT),
                lambda: holdout_engine.resolve_output(symlink, ROOT),
            ):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    resolver()
            for resolver in (
                lambda: corpus_engine.resolve_output_path(
                    ROOT / "g013-forbidden-output", plugin=ROOT
                ),
                lambda: holdout_engine.resolve_output(
                    ROOT / "g013-forbidden-holdout", ROOT
                ),
            ):
                with self.assertRaisesRegex(ValueError, "repository|source"):
                    resolver()

    def test_g013_evidence_commit_strictly_postdates_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            self._git(repo, "config", "user.name", "G013 Test")
            self._git(repo, "config", "user.email", "g013@example.invalid")
            marker = repo / "marker.txt"
            marker.write_text("before\n", encoding="utf-8")
            self._git(repo, "add", "marker.txt")
            self._git(repo, "commit", "-m", "before source")
            before = self._git(repo, "rev-parse", "HEAD")
            marker.write_text("source\n", encoding="utf-8")
            self._git(repo, "commit", "-am", "source")
            source = self._git(repo, "rev-parse", "HEAD")
            marker.write_text("evidence\n", encoding="utf-8")
            self._git(repo, "commit", "-am", "evidence")
            evidence = self._git(repo, "rev-parse", "HEAD")
            ledger_engine.validate_evidence_commit(
                repo, source_commit=source, evidence_commit=evidence
            )
            with self.assertRaisesRegex(ValueError, "descend"):
                ledger_engine.validate_evidence_commit(
                    repo, source_commit=source, evidence_commit=before
                )
            with self.assertRaisesRegex(ValueError, "strictly postdate"):
                ledger_engine.validate_evidence_commit(
                    repo, source_commit=source, evidence_commit=source
                )

    def test_g013_recovery_binding_rejects_every_identity_replacement(self) -> None:
        capability, _report, binding = self._capability()
        case_path = ROOT / "evaluation" / "cases" / "pre-freeze-compaction.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        native = case["fixture"]["native_compaction_resume"]
        self.assertIn("prepare_prompt", native)
        self.assertIn("fresh_recovery_prompt", native)
        self.assertIn("no-summary/no-handle", native["fresh_recovery_prompt"])
        self.assertIs(live._rebind_capability(capability, binding), capability)
        for field in (
            "task_id",
            "root_task_id",
            "executor_task_id",
            "owner_label",
            "destination_id",
            "lineage_digest",
            "role_config_digest",
            "session_id",
            "thread_id",
            "permission_digest",
            "claim_digest",
        ):
            changed = dict(binding)
            changed[field] = (
                "f" * 64 if field.endswith("_digest") else f"replacement-{field}"
            )
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "capability"
            ):
                live._rebind_capability(capability, changed)

    def test_g013_old_evidence_and_legacy_generation_are_absent(self) -> None:
        evidence = ROOT / "evaluation" / "results" / "evidence"
        self.assertEqual(list(evidence.glob("*.json")), [])
        active = json.loads(
            (ROOT / "evaluation" / "results" / "current.json").read_text(
                encoding="utf-8"
            )
        )
        invalid = copy.deepcopy(active)
        invalid["engine_generation"] = "0.5"
        with self.assertRaisesRegex(ValueError, "generation|envelope"):
            validate_ledger(invalid, repo=ROOT)
        invalid = copy.deepcopy(active)
        invalid["accepted_evidence"] = [{"generation": "0.4"}]
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_ledger(invalid, repo=ROOT)
        invalid = copy.deepcopy(active)
        invalid["certification"] = {"offline": True}
        with self.assertRaisesRegex(ValueError, "certification"):
            validate_ledger(invalid, repo=ROOT)


if __name__ == "__main__":
    unittest.main()
