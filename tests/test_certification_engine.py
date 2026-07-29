from __future__ import annotations

import copy
import hashlib
import inspect
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
    "evaluation/core/schema.py",
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
    ledger = {
        "schema_version": 1,
        "engine_generation": "0.6",
        "state": "refresh_required",
        "snapshot": current,
        "source_anchor": None,
        "planned_impact": None,
        "planned_invocations": {
            "executor": None, "corpus": None, "holdout": None,
        },
        "cost": {"executor": None, "corpus": None, "holdout": None},
        "authorities": {"executor": None, "corpus": None, "holdout": None},
        "accepted_evidence": {
            slot: None for slot in ledger_engine.EVIDENCE_SLOTS
        },
        "coverage": {},
        "receipt_head": None,
        "freeze": None,
        "certification": None,
    }
    impact = plan_impact(
        current, current, pending=ledger_engine.derive_pending(ledger)
    )
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


def runtime_records(
    report: object,
    authority: object,
    binding: dict[str, str],
    repo: Path,
    *,
    gate: str = "corpus",
    units: tuple[str, ...] = ("unit",),
) -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    next_action = report.to_wire()["next_action"]
    action = {
        "kind": next_action["kind"],
        "target": next_action["target"],
        "scope": next_action["scope"],
        "progress_key": report.to_wire()["progress_key"],
        "attempt_key": make_attempt_key(report).value,
    }
    plan = {
        "schema_version": 1,
        "repo": str(repo.resolve()),
        "gate": gate,
        "phase": "calibration" if gate == "executor" else "evaluation",
        "impact_token": "a" * 64,
        "action": action,
        "task_binding_sha256": canonical_sha256(dict(report.facts.task.to_value())),
        "role_config_sha256": binding["role_config_digest"],
        "profile": {
            "binary": "codex",
            "model": "gpt-5.6-sol",
            "effort": "high",
            "timeout_ms": 300_000,
            "arm": "blinded-pair" if gate == "holdout" else "candidate",
            "prompt_sha256": "b" * 64,
        },
        "template": {
            "argv": ["true", "{unit}"],
            "cwd": str(repo.resolve()),
            "env": {"LC_ALL": "C"},
            "timeout_ms": 300_000,
        },
        "output": str((repo.parent / f"{gate}-output").resolve()),
        "units": sorted(units),
        "resource_digests": ["c" * 64],
        "cost_sha256": "d" * 64,
    }
    plan["invocation_sha256"] = canonical_sha256(plan)
    record = {
        "schema_version": 1,
        "gate": gate,
        "phase": plan["phase"],
        "impact_token": plan["impact_token"],
        "invocation_sha256": plan["invocation_sha256"],
        "action": action,
        "request_sha256": "e" * 64,
        "affirmative_sha256": "f" * 64,
        "host": {
            "task_id": binding["task_id"],
            "message_id": binding["message_id"],
            "turn_id": binding["turn_id"],
            "content_sha256": binding["content_digest"],
            "role_config_sha256": binding["role_config_digest"],
        },
    }
    record["authority_sha256"] = canonical_sha256(record)
    bound = dict(binding)
    bound["permission_digest"] = live._permission_digest(report, authority, plan)
    bound["claim_digest"] = live._claim_digest(plan)
    return plan, record, bound


def preflight_gate(capability: object) -> object:
    plan, profile = capability._plan, capability._plan["profile"]
    return live._preflight_effect(
        capability,
        gate=plan["gate"],
        output=Path(plan["output"]),
        units=list(plan["units"]),
        model=profile["model"],
        effort=profile["effort"],
        timeout_ms=profile["timeout_ms"],
        arm=profile["arm"],
    )


def g013_claim_worker(
    claim_root: str,
    key: str,
    start: object,
    results: object,
) -> None:
    start.wait()
    try:
        live._claim_file(Path(claim_root), key)
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
                "planned_impact",
                "planned_invocations",
                "cost",
                "authorities",
                "accepted_evidence",
                "coverage",
                "receipt_head",
                "freeze",
                "certification",
            },
        )
        self.assertEqual(active["schema_version"], 1)
        self.assertEqual(active["engine_generation"], "0.6")
        self.assertEqual(active["state"], "refresh_required")
        self.assertIsNone(active["source_anchor"])
        pending = ledger_engine.derive_pending(active)
        self.assertEqual(pending["gates"], list(ledger_engine.PENDING_GATES))
        self.assertEqual(pending["corpus_cases"], sorted(active["snapshot"]["corpus"]["cases"]))
        self.assertEqual(pending["holdout_pairs"], sorted(active["snapshot"]["holdout"]["pairs"])[:1])
        self.assertEqual(
            active["authorities"],
            {"executor": None, "corpus": None, "holdout": None},
        )
        self.assertTrue(all(value is None for value in active["accepted_evidence"].values()))
        self.assertIsNone(active["planned_impact"])
        self.assertTrue(all(value is None for value in active["planned_invocations"].values()))
        self.assertTrue(all(value is None for value in active["cost"].values()))
        self.assertEqual(active["coverage"], {})
        self.assertIsNone(active["receipt_head"])
        self.assertIsNone(active["freeze"])
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
        self.assertTrue(all(value is None for value in active["accepted_evidence"].values()))
        self.assertFalse(
            any(
                "evaluation/results/evidence" in json.dumps(value)
                for value in active.values()
            )
        )

    def test_active_producers_and_validators_are_generation_6_only(self) -> None:
        from evaluation.holdout import engine as holdout_engine

        receipt = (ROOT / "evaluation/core/receipt.py").read_text(encoding="utf-8")
        self.assertNotIn('"engine_generation": "0.4"', receipt)
        for relative in (
            "evaluation/corpus/engine.py",
            "evaluation/holdout/engine.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn('"engine_generation": "0.4"', source)
            self.assertNotIn("unavailable until Batch3", source)
        self.assertTrue(callable(corpus_engine.run_authorized))
        self.assertTrue(callable(holdout_engine.run_authorized))
        validator = (ROOT / "evaluation/core/ledger.py").read_text(encoding="utf-8")
        self.assertNotIn('engine_generation") != "0.4"', validator)
        args = cli.build_parser().parse_args(["executor", "--dry-run"])
        with mock.patch("builtins.print") as output:
            self.assertEqual(cli.executor_command(args), 0)
        self.assertEqual(json.loads(output.call_args.args[0])["schema_generation"], 6)

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
        self.assertEqual(len(CORPUS_SEMANTIC_PATHS), 7)
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

            with self.assertRaisesRegex(
                IdentityError, "invalid case envelope|schema object mismatch"
            ):
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

            with self.assertRaisesRegex(
                IdentityError, "holdout pair envelope|schema object mismatch"
            ):
                build_snapshot(clone)

    def test_unknown_snapshot_dimension_fails_closed(self) -> None:
        changed = copy.deepcopy(self.snapshot)
        changed["unknown"] = {"value": True}
        with self.assertRaisesRegex(
            IdentityError, "unknown snapshot field|schema object mismatch"
        ):
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
        self.assertTrue(all(value is None for value in ledger["accepted_evidence"].values()))
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
        final = {
            "decision": "continue",
            "qualifies": False,
            "execplan_condition": "not_required",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": [],
            "reason": "bound",
            "recovery_state": None,
        }
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
        with self.assertRaisesRegex(ValueError, "pre-anchor|certification"):
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
                with self.assertRaisesRegex(ValueError, "phase proof"):
                    corpus_engine.invoke_codex(object())
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
        with self.assertRaisesRegex(ValueError, "pre-anchor|certification"):
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
        self.assertEqual(impact.returncode, 2, impact.stderr)
        impact_payload = json.loads(impact.stdout)
        self.assertEqual(impact_payload["snapshot"], build_snapshot(ROOT))
        self.assertEqual(impact_payload["planned_impact"], expected_impact)
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

    def _plan_only(self) -> dict[str, object]:
        ledger = self._lifecycle(certified=False)
        ledger["authorities"] = {gate: None for gate in ledger_engine.LIVE_SLOTS}
        for field in ("planned_invocations", "cost"):
            ledger[field]["corpus"] = None
            ledger[field]["holdout"] = None
        ledger["accepted_evidence"] = {
            slot: None for slot in ledger_engine.EVIDENCE_SLOTS
        }
        ledger.update(coverage={}, receipt_head=None, freeze=None, certification=None)
        return ledger

    def _capability(
        self,
        repo: Path = ROOT,
        *,
        units: tuple[str, ...] = ("unit",),
        resource_digests: tuple[str, ...] = ("b" * 64, "c" * 64),
    ) -> tuple[object, object, dict[str, str]]:
        report, authority, binding = g013_authority_fixture()
        plan, record, binding = runtime_records(
            report, authority, binding, repo, units=units
        )
        plan["resource_digests"] = sorted(resource_digests)
        plan["invocation_sha256"] = canonical_sha256({
            key: value for key, value in plan.items() if key != "invocation_sha256"
        })
        record["invocation_sha256"] = plan["invocation_sha256"]
        record["authority_sha256"] = canonical_sha256({
            key: value for key, value in record.items() if key != "authority_sha256"
        })
        binding["claim_digest"] = live._claim_digest(plan)
        issue = getattr(live, "_issue_trusted_host_context")
        context = issue(authority, binding, plan, record)
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
        with self.assertRaisesRegex(ValueError, "source anchor|schema object mismatch"):
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
        plan, record, binding = runtime_records(
            report, authority, binding, ROOT
        )
        context = issue(authority, binding, plan, record)
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
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            root = self._claim_root(repo)
            capability, _report, _binding = self._capability(repo)
            order: list[str] = []

            def claim(_root: Path, key: str) -> None:
                self.assertEqual(_root, root)
                order.append(key.split("-", 1)[0])

            with mock.patch.object(live, "_claim_file", side_effect=claim):
                claimed = live._claim_effect_set(preflight_gate(capability))
                unit = live._claim_units(claimed, ["unit"])["unit"]
                live._issue_phase_proof(unit)
            self.assertEqual(
                order,
                [
                    "authority",
                    "attempt",
                    "resource",
                    "resource",
                    "output",
                    "unit",
                    "phase",
                ],
            )

        for fail_after in range(1, 6):
            with self.subTest(fail_after=fail_after), tempfile.TemporaryDirectory() as raw:
                repo = Path(raw) / "repo"
                repo.mkdir()
                self._git(repo, "init")
                root = self._claim_root(repo)
                capability, _report, _binding = self._capability(repo)
                real_claim = live._claim_file
                count = 0

                def fault(
                    claim_root: Path,
                    key: str,
                ) -> None:
                    nonlocal count
                    real_claim(claim_root, key)
                    count += 1
                    if count == fail_after:
                        raise RuntimeError("injected claim failure")

                with (
                    mock.patch.object(live, "_claim_file", side_effect=fault),
                    self.assertRaisesRegex(RuntimeError, "injected"),
                ):
                    live._claim_effect_set(preflight_gate(capability))
                self.assertEqual(len(list(root.iterdir())), fail_after)

    def test_g013_phase_claim_collision_prevents_model_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            self._claim_root(repo)
            capability, _report, _binding = self._capability(
                repo, resource_digests=("b" * 64,)
            )
            claimed = live._claim_effect_set(preflight_gate(capability))
            unit = live._claim_units(claimed, ["unit"])["unit"]
            live._issue_phase_proof(unit)
            with self.assertRaises(FileExistsError):
                live._issue_phase_proof(unit)

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
        with self.assertRaisesRegex(
            ValueError, "pre-anchor|evidence|schema type or enum mismatch"
        ):
            validate_ledger(invalid, repo=ROOT)
        invalid = copy.deepcopy(active)
        invalid["certification"] = {"offline": True}
        with self.assertRaisesRegex(ValueError, "pre-anchor|certification"):
            validate_ledger(invalid, repo=ROOT)


class Batch3SourceRepairRegressionTests(unittest.TestCase):
    PUBLIC_BASELINE = {
        "arm": "public-0.2",
        "source_commit": "3b9c11fac1f97df75263e0bfc6421c575e04e8b2",
        "source_tree": "4708ebc12f74d4482764796fdd00f1fa7194a13a",
        "artifact_sha256": (
            "77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89"
        ),
        "semantic_sha256": (
            "fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4"
        ),
        "skill_entries": [
            "SKILL.md",
            "agents/openai.yaml",
            "references/external-review.md",
            "references/task-packets.md",
        ],
    }

    @staticmethod
    def _sealed(payload: dict[str, object], field: str) -> dict[str, object]:
        result = copy.deepcopy(payload)
        result[field] = canonical_sha256(result)
        return result

    def _lifecycle(self, *, certified: bool) -> dict[str, object]:
        snapshot = build_snapshot(ROOT)
        self.assertEqual(snapshot["public_baseline"], self.PUBLIC_BASELINE)
        anchor = {
            "source_commit": "1" * 40,
            "source_tree": "2" * 40,
            "package_artifact_sha256": snapshot["package"]["artifact_sha256"],
            "package_semantic_sha256": snapshot["package"]["semantic_sha256"],
            "engine_manifest_sha256": snapshot["engine"]["manifest_sha256"],
            "executor_role_sha256": snapshot["role"]["executor_sha256"],
            "public_baseline_sha256": canonical_sha256(self.PUBLIC_BASELINE),
        }
        scope = {
            "gates": list(ledger_engine.PENDING_GATES),
            "corpus_cases": sorted(snapshot["corpus"]["cases"]),
            "holdout_pairs": sorted(snapshot["holdout"]["pairs"]),
            "adaptive_policy_sha256": "3" * 64,
        }
        planned_impact = self._sealed(
            {
                "schema_version": 1,
                "snapshot_sha256": canonical_sha256(snapshot),
                "source_anchor_sha256": canonical_sha256(anchor),
                "initial_scope": scope,
                "initial_scope_sha256": canonical_sha256(scope),
                "live_calls": {"min": 1, "max": 43},
            },
            "impact_token",
        )
        action = {
            "kind": "RECONCILE",
            "target": "gate:g015",
            "scope": "family:g015",
            "progress_key": "4" * 64,
            "attempt_key": "5" * 64,
        }
        costs: dict[str, dict[str, object]] = {}
        invocations: dict[str, dict[str, object]] = {}
        authorities: dict[str, dict[str, object]] = {}
        evidence: dict[str, dict[str, object]] = {}
        executor_receipt: str | None = None
        for gate in ("executor", "corpus", "holdout"):
            basis = "source-derived" if gate == "executor" else "executor-calibration"
            cost = self._sealed(
                {
                    "schema_version": 1,
                    "gate": gate,
                    "basis": basis,
                    "basis_sha256": "6" * 64,
                    "basis_receipt_sha256": None if gate == "executor" else executor_receipt,
                    "model_calls": {"min": 1, "max": 1 if gate == "executor" else 20},
                    "uncached_input_tokens": {"min": 1, "max": 1000},
                    "output_tokens": {"min": 1, "max": 1000},
                    "combined_tokens": {"min": 2, "max": 2000},
                    "wall_milliseconds": {"min": 1, "max": 300_000},
                },
                "cost_sha256",
            )
            costs[gate] = cost
            units = (
                ["subthreshold-control"]
                if gate == "executor"
                else sorted(
                    snapshot["corpus"]["cases"]
                    if gate == "corpus"
                    else snapshot["holdout"]["pairs"]
                )
            )
            invocation = self._sealed(
                {
                    "schema_version": 1,
                    "gate": gate,
                    "phase": "calibration" if gate == "executor" else "evaluation",
                    "impact_token": planned_impact["impact_token"],
                    "action": action,
                    "task_binding_sha256": "3" * 64,
                    "role_config_sha256": snapshot["role"]["executor_sha256"],
                    "profile": {
                        "binary": "codex",
                        "model": "gpt-5.6-sol",
                        "effort": "high",
                        "timeout_ms": 300_000,
                        "arm": "candidate" if gate != "holdout" else "blinded-pair",
                        "prompt_sha256": "7" * 64,
                    },
                    "template": {
                        "argv": ["codex", "exec", "{unit}"],
                        "cwd": str(ROOT),
                        "env": {"LC_ALL": "C"},
                        "timeout_ms": 300_000,
                    },
                    "repo": str(ROOT),
                    "output": f"/tmp/happycodex-g015-{gate}",
                    "units": units,
                    "resource_digests": ["8" * 64],
                    "cost_sha256": cost["cost_sha256"],
                },
                "invocation_sha256",
            )
            invocations[gate] = invocation
            authority = self._sealed(
                {
                    "schema_version": 1,
                    "gate": gate,
                    "phase": invocation["phase"],
                    "impact_token": planned_impact["impact_token"],
                    "invocation_sha256": invocation["invocation_sha256"],
                    "action": action,
                    "request_sha256": "5" * 64,
                    "affirmative_sha256": "6" * 64,
                    "host": {
                        "task_id": "task-g015",
                        "message_id": "message-g015",
                        "turn_id": "turn-g015",
                        "content_sha256": "7" * 64,
                        "role_config_sha256": snapshot["role"]["executor_sha256"],
                    },
                },
                "authority_sha256",
            )
            authorities[gate] = authority
            if gate == "executor":
                executor_receipt = "pending"
        parent: str | None = None
        specs = (
            ("executor_calibration", "executor", ["subthreshold-control"]),
            ("corpus_summary", "corpus", sorted(snapshot["corpus"]["cases"])),
            ("holdout_summary", "holdout", sorted(snapshot["holdout"]["pairs"])[:2]),
            ("offline_summary", "receipt", []),
            ("review_summary", "review", []),
            ("offline_summary", "isolated_install", []),
        )
        for index, (kind, gate, units) in enumerate(specs):
            bound_gate = gate if gate in invocations else None
            record = self._sealed(
                {
                    "schema_version": 1,
                    "kind": kind,
                    "gate": gate,
                    "sequence": index,
                    "evidence_commit": f"{index + 10:040x}",
                    "path": (
                        "evaluation/results/evidence/"
                        f"{index + 30:064x}.json"
                    ),
                    "blob": f"{index + 20:040x}",
                    "content_sha256": f"{index + 30:064x}",
                    "impact_token": planned_impact["impact_token"],
                    "invocation_sha256": (
                        invocations[bound_gate]["invocation_sha256"]
                        if bound_gate
                        else None
                    ),
                    "authority_sha256": (
                        authorities[bound_gate]["authority_sha256"]
                        if bound_gate
                        else None
                    ),
                    "units": units,
                    "transcript": (
                        [
                            {
                                "pair_id": pair,
                                "outcome": "equal",
                                "receipt_sha256": f"{index + offset + 90:064x}",
                            }
                            for offset, pair in enumerate(units)
                        ]
                        if gate == "holdout"
                        else []
                    ),
                    "actual": (
                        {
                            "model_calls": 1,
                            "uncached_input_tokens": 10,
                            "output_tokens": 5,
                            "combined_tokens": 15,
                            "wall_milliseconds": 1000,
                        }
                        if gate == "executor"
                        else None
                    ),
                    "producer": {
                        "schema_version": 1,
                        "output_schema_sha256": canonical_sha256(
                            corpus_engine.OUTPUT_SCHEMA
                        ),
                    },
                    "subject": {
                        "schema_version": 1,
                        "gate": gate,
                        "source_anchor_sha256": canonical_sha256(anchor),
                        "snapshot_sha256": canonical_sha256(snapshot),
                    },
                    "pre_effect_grant_sha256": (
                        authorities[bound_gate]["authority_sha256"]
                        if bound_gate
                        else "9" * 64
                    ),
                    "parent_receipt_sha256": parent,
                },
                "receipt_sha256",
            )
            parent = record["receipt_sha256"]
            evidence[gate] = record
            if gate == "executor":
                executor_receipt = record["receipt_sha256"]
                for later in ("corpus", "holdout"):
                    costs[later]["basis_receipt_sha256"] = executor_receipt
                    costs[later]["cost_sha256"] = canonical_sha256({
                        key: value for key, value in costs[later].items()
                        if key != "cost_sha256"
                    })
                    invocations[later]["cost_sha256"] = costs[later]["cost_sha256"]
                    invocations[later]["invocation_sha256"] = canonical_sha256({
                        key: value for key, value in invocations[later].items()
                        if key != "invocation_sha256"
                    })
                    authorities[later]["invocation_sha256"] = invocations[later]["invocation_sha256"]
                    authorities[later]["authority_sha256"] = canonical_sha256({
                        key: value for key, value in authorities[later].items()
                        if key != "authority_sha256"
                    })
        coverage = ledger_engine.derive_coverage(snapshot, evidence)
        freeze = self._sealed(
            {
                "schema_version": 1,
                "source_anchor_sha256": canonical_sha256(anchor),
                "receipt_head": evidence["receipt"]["receipt_sha256"],
                "coverage_sha256": coverage["coverage_sha256"],
            },
            "freeze_sha256",
        ) if certified else None
        certification = None
        state = "refresh_required"
        if certified:
            certification = self._sealed(
                {
                    "schema_version": 1,
                    "source_anchor_sha256": canonical_sha256(anchor),
                    "snapshot_sha256": canonical_sha256(snapshot),
                    "role_config_sha256": snapshot["role"]["executor_sha256"],
                    "authorities": {
                        gate: item["authority_sha256"]
                        for gate, item in authorities.items()
                    },
                    "executor_evidence_sha256": evidence["executor"]["receipt_sha256"],
                    "evidence_receipts": [
                        item["receipt_sha256"]
                        for item in sorted(evidence.values(), key=lambda item: item["sequence"])
                    ],
                    "coverage_sha256": coverage["coverage_sha256"],
                    "freeze_sha256": freeze["freeze_sha256"],
                    "receipt_head": parent,
                },
                "certification_sha256",
            )
            state = "certified"
        return {
            "schema_version": 1,
            "engine_generation": "0.6",
            "state": state,
            "snapshot": snapshot,
            "source_anchor": anchor,
            "planned_impact": planned_impact,
            "planned_invocations": invocations,
            "cost": costs,
            "authorities": authorities,
            "accepted_evidence": evidence,
            "coverage": coverage,
            "receipt_head": parent,
            "freeze": freeze,
            "certification": certification,
        }

    def _claim_root(self, repo: Path) -> Path:
        raw = Path(self._git(repo, "rev-parse", "--git-common-dir"))
        common = raw if raw.is_absolute() else repo / raw
        root = common.resolve() / "happycodex" / "effect-claims" / "v6"
        root.mkdir(parents=True)
        root.chmod(0o700)
        return root

    def _plan_only(self) -> dict[str, object]:
        ledger = self._lifecycle(certified=False)
        ledger["authorities"] = {gate: None for gate in ledger_engine.LIVE_SLOTS}
        for field in ("planned_invocations", "cost"):
            ledger[field]["corpus"] = None
            ledger[field]["holdout"] = None
        ledger["accepted_evidence"] = {
            slot: None for slot in ledger_engine.EVIDENCE_SLOTS
        }
        ledger.update(coverage={}, receipt_head=None, freeze=None, certification=None)
        return ledger

    def _gate(
        self, repo: Path, *, gate: str = "corpus", units: tuple[str, ...] = ("unit",)
    ) -> object:
        report, authority, binding = g013_authority_fixture()
        plan, record, binding = runtime_records(
            report, authority, binding, repo, gate=gate, units=units
        )
        issue = getattr(live, "_issue_trusted_host_context")
        context = issue(authority, binding, plan, record)
        with mock.patch.object(live, "_trusted_host_context", return_value=context):
            return live._authorize_effect(report, object())

    def _git(self, repo: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _repo(self, raw: str) -> tuple[Path, Path]:
        repo = Path(raw) / "repo"
        repo.mkdir()
        self._git(repo, "init")
        return repo, self._claim_root(repo)

    def test_public_02_archive_identity_and_surface_are_exact(self) -> None:
        from evaluation.core import identity

        self.assertEqual(identity.PUBLIC_02_ARM, "public-0.2")
        self.assertEqual(identity.PUBLIC_02_SOURCE_COMMIT, self.PUBLIC_BASELINE["source_commit"])
        self.assertEqual(identity.PUBLIC_02_SOURCE_TREE, self.PUBLIC_BASELINE["source_tree"])
        self.assertEqual(
            identity.PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
            self.PUBLIC_BASELINE["artifact_sha256"],
        )
        self.assertEqual(
            identity.PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
            self.PUBLIC_BASELINE["semantic_sha256"],
        )
        self.assertEqual(
            list(identity.PUBLIC_02_SKILL_ENTRIES),
            self.PUBLIC_BASELINE["skill_entries"],
        )

    def test_no_public_04_arm_or_receipt_field_survives(self) -> None:
        production = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "evaluation").rglob("*.py"))
        )
        for retired in ("public-0.4", "PUBLIC_040", "public_0_4_0"):
            self.assertNotIn(retired, production)

    def test_anchored_refresh_accepts_exact_plans_costs_and_authorities(self) -> None:
        validate_ledger(self._plan_only())

    def test_certification_requires_exact_post_source_evidence(self) -> None:
        certified = self._lifecycle(certified=True)
        with self.assertRaisesRegex(ValueError, "repository|repo"):
            validate_ledger(certified)

    def test_impact_replays_persisted_plan_while_null_genesis_fails_closed(self) -> None:
        anchored = self._plan_only()
        replay = ledger_engine.replay_planned_lifecycle(anchored)
        self.assertEqual(replay["impact_token"], anchored["planned_impact"]["impact_token"])
        genesis = copy.deepcopy(anchored)
        genesis.update(
            planned_impact=None,
            planned_invocations={gate: None for gate in ledger_engine.LIVE_SLOTS},
            cost={gate: None for gate in ledger_engine.LIVE_SLOTS},
            authorities={"executor": None, "corpus": None, "holdout": None},
            accepted_evidence={
                slot: None for slot in ledger_engine.EVIDENCE_SLOTS
            },
            coverage={},
            receipt_head=None,
            freeze=None,
            certification=None,
        )
        with self.assertRaisesRegex(ValueError, "planned|refresh"):
            ledger_engine.replay_planned_lifecycle(genesis)

    def test_claims_use_only_capability_derived_authority_and_attempt(self) -> None:
        self.assertFalse(hasattr(live, "_ClaimRequest"))
        with tempfile.TemporaryDirectory() as raw:
            repo, _root = self._repo(raw)
            gate = self._gate(repo)
            descriptor = gate.descriptor()
            self.assertEqual(set(descriptor), {
                "attempt_id", "authority_sha256", "binding_sha256",
                "gate", "invocation_sha256",
            })
            claimed = live._claim_effect_set(preflight_gate(gate))
            self.assertEqual(claimed.descriptor(), descriptor)

    def test_partial_or_reused_claim_set_stops_before_another_claim_or_effect(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo, root = self._repo(raw)
            gate = self._gate(repo)
            preflight = preflight_gate(gate)
            claims = live._effect_claim_specs(preflight)
            kind, digest = claims[1]
            live._claim_file(root, f"{kind}-{digest}")
            before = sorted(path.name for path in root.iterdir())
            with self.assertRaises(FileExistsError):
                live._claim_effect_set(preflight)
            self.assertEqual(sorted(path.name for path in root.iterdir()), before)

    def test_unclaimed_capability_cannot_create_case_pair_mapping_fixture_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo, _root = self._repo(raw)
            gate = self._gate(repo)
            target = repo.parent / "forbidden"
            with self.assertRaisesRegex(ValueError, "claimed|unit"):
                live._claim_unit(gate, "unit")
            with self.assertRaisesRegex(ValueError, "unit"):
                live._require_unit_capability(gate, "unit")
            self.assertFalse(target.exists())

    def test_phase_proof_is_exact_one_shot_and_gate_capability_cannot_invoke(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo, _root = self._repo(raw)
            gate = self._gate(repo)
            claimed = live._claim_effect_set(preflight_gate(gate))
            unit = live._claim_unit(claimed, "unit")
            with self.assertRaisesRegex(ValueError, "phase proof"):
                corpus_engine.invoke_codex(gate)
            proof = live._issue_phase_proof(unit)
            completed = subprocess.CompletedProcess([], 0, "", "")
            with mock.patch.object(corpus_engine, "run", return_value=completed) as runner:
                corpus_engine.invoke_codex(proof)
                with self.assertRaisesRegex(ValueError, "spent"):
                    corpus_engine.invoke_codex(proof)
            runner.assert_called_once()

    def _assert_effect_order(self, gate_name: str) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo, root = self._repo(raw)
            unit_id = f"{gate_name}-unit"
            gate = self._gate(repo, gate=gate_name, units=(unit_id,))
            claimed = live._claim_effect_set(preflight_gate(gate))
            before = sorted(path.name for path in root.iterdir())
            unit = live._claim_unit(claimed, unit_id)
            after = sorted(path.name for path in root.iterdir())
            self.assertGreater(len(after), len(before))
            self.assertTrue(any(name.startswith("unit-") for name in after))
            live._require_unit_capability(unit, unit_id)
            effect = repo.parent / f"{gate_name}-effect"
            effect.mkdir()
            self.assertTrue(effect.is_dir())

    def test_executor_effect_order_in_fresh_temp_repo(self) -> None:
        self._assert_effect_order("executor")

    def test_corpus_effect_order_in_fresh_temp_repo(self) -> None:
        self._assert_effect_order("corpus")

    def test_holdout_effect_order_in_fresh_temp_repo(self) -> None:
        self._assert_effect_order("holdout")

    def test_semantic_projection_rejects_unknown_top_level_result_fields(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": False,
            "execplan_condition": "not_required",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": [],
            "reason": "bounded",
            "recovery_state": None,
        }
        self.assertEqual(corpus_engine.validate_output_result(result), result)
        with self.assertRaisesRegex(ValueError, "top-level"):
            corpus_engine.validate_output_result({**result, "extra": True})

    def test_offline_summary_requires_exact_gate_evidence_generation6(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        offline = lifecycle["accepted_evidence"]["receipt"]
        ledger_engine.validate_evidence_record(
            offline,
            lifecycle["snapshot"],
            lifecycle["planned_impact"],
            lifecycle["planned_invocations"],
            lifecycle["authorities"],
        )
        invalid = copy.deepcopy(offline)
        invalid["content_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "receipt|evidence"):
            ledger_engine.validate_evidence_record(
                invalid,
                lifecycle["snapshot"],
                lifecycle["planned_impact"],
                lifecycle["planned_invocations"],
                lifecycle["authorities"],
            )

    def test_corpus_summary_accepts_only_the_exact_authorized_subset_generation6(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        corpus = lifecycle["accepted_evidence"]["corpus"]
        ledger_engine.validate_evidence_record(
            corpus,
            lifecycle["snapshot"],
            lifecycle["planned_impact"],
            lifecycle["planned_invocations"],
            lifecycle["authorities"],
        )
        invalid = copy.deepcopy(corpus)
        invalid["units"] = invalid["units"][:-1]
        with self.assertRaisesRegex(ValueError, "scope|units|receipt"):
            ledger_engine.validate_evidence_record(
                invalid,
                lifecycle["snapshot"],
                lifecycle["planned_impact"],
                lifecycle["planned_invocations"],
                lifecycle["authorities"],
            )

    def test_coverage_is_derived_exactly_once_without_prior_or_waiver(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        self.assertEqual(
            ledger_engine.derive_coverage(
                lifecycle["snapshot"], lifecycle["accepted_evidence"]
            ),
            lifecycle["coverage"],
        )
        with self.assertRaisesRegex(ValueError, "prior|waiv|coverage"):
            ledger_engine.derive_coverage(
                lifecycle["snapshot"],
                lifecycle["accepted_evidence"],
                prior={"corpus": "waived"},
            )

    def test_partial_dag_states_and_successor_are_exact(self) -> None:
        plan_only = self._lifecycle(certified=False)
        plan_only["authorities"] = {
            "executor": None,
            "corpus": None,
            "holdout": None,
        }
        for field in ("planned_invocations", "cost"):
            plan_only[field]["corpus"] = None
            plan_only[field]["holdout"] = None
        plan_only["accepted_evidence"] = {
            slot: None for slot in ledger_engine.EVIDENCE_SLOTS
        }
        plan_only["coverage"] = {}
        plan_only["receipt_head"] = None
        plan_only["freeze"] = None
        validate_ledger(plan_only)
        successor = copy.deepcopy(plan_only)
        successor["authorities"]["executor"] = self._lifecycle(
            certified=False
        )["authorities"]["executor"]
        ledger_engine.validate_successor(plan_only, successor)
        with self.assertRaisesRegex(ValueError, "rollback|immutable|successor"):
            ledger_engine.validate_successor(successor, plan_only)

    def test_executor_evidence_is_single_calibration_and_later_cost_basis(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        self.assertNotIn("calibration_history", lifecycle)
        executor = lifecycle["accepted_evidence"]["executor"]
        self.assertEqual(executor["kind"], "executor_calibration")
        self.assertEqual(
            lifecycle["cost"]["corpus"]["basis_receipt_sha256"],
            executor["receipt_sha256"],
        )
        invalid = copy.deepcopy(lifecycle)
        invalid["cost"]["corpus"]["basis"] = "source-derived"
        invalid["cost"]["corpus"]["cost_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in invalid["cost"]["corpus"].items()
                if key != "cost_sha256"
            }
        )
        with self.assertRaisesRegex(ValueError, "calibration|basis"):
            validate_ledger(invalid)

    def test_evidence_slot_kind_coverage_sequence_and_chain_are_exact(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        evidence = lifecycle["accepted_evidence"]
        self.assertEqual(
            set(evidence),
            {
                "executor",
                "corpus",
                "holdout",
                "receipt",
                "review",
                "isolated_install",
            },
        )
        invalid = copy.deepcopy(lifecycle)
        invalid["accepted_evidence"]["corpus"]["kind"] = "review_summary"
        with self.assertRaisesRegex(ValueError, "kind|slot|evidence"):
            ledger_engine.validate_evidence_record(
                invalid["accepted_evidence"]["corpus"],
                invalid["snapshot"],
                invalid["planned_impact"],
                invalid["planned_invocations"],
                invalid["authorities"],
                slot="corpus",
            )
        duplicate = copy.deepcopy(lifecycle)
        duplicate["accepted_evidence"]["review"] = copy.deepcopy(
            duplicate["accepted_evidence"]["receipt"]
        )
        with self.assertRaisesRegex(ValueError, "duplicate|sequence|receipt|slot"):
            ledger_engine.derive_coverage(
                duplicate["snapshot"], duplicate["accepted_evidence"]
            )

    def test_git_evidence_binds_commit_path_blob_bytes_content_producer_subject(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            self._git(repo, "init")
            self._git(repo, "config", "user.name", "HappyCodex Test")
            self._git(repo, "config", "user.email", "happycodex@example.invalid")
            (repo / "source.txt").write_text("source\n", encoding="utf-8")
            self._git(repo, "add", "source.txt")
            self._git(repo, "commit", "-m", "source")
            source_commit = self._git(repo, "rev-parse", "HEAD")
            producer = {"kind": "corpus", "digest": "a" * 64}
            subject = {"gate": "corpus", "digest": "b" * 64}
            summary = {
                "schema_version": 1,
                "producer": producer,
                "subject": subject,
            }
            content = (
                json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode()
            digest = hashlib.sha256(content).hexdigest()
            relative = f"evaluation/results/evidence/{digest}.json"
            path = repo / relative
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
            self._git(repo, "add", relative)
            self._git(repo, "commit", "-m", "evidence")
            evidence_commit = self._git(repo, "rev-parse", "HEAD")
            blob = self._git(repo, "rev-parse", f"HEAD:{relative}")
            verified = ledger_engine.verify_evidence_object(
                repo,
                source_commit=source_commit,
                evidence_commit=evidence_commit,
                path=relative,
                blob=blob,
                content_sha256=digest,
                producer=producer,
                subject=subject,
            )
            self.assertEqual(verified, summary)
            with self.assertRaisesRegex(ValueError, "blob|content|evidence"):
                ledger_engine.verify_evidence_object(
                    repo,
                    source_commit=source_commit,
                    evidence_commit=evidence_commit,
                    path=relative,
                    blob="f" * 40,
                    content_sha256=digest,
                    producer=producer,
                    subject=subject,
                )

    def test_recursive_output_schema_rejects_nested_drift(self) -> None:
        result = {
            "decision": "continue",
            "qualifies": False,
            "execplan_condition": "not_required",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": False,
            "finding_classifications": [
                {
                    "identity": "finding",
                    "domain": "other",
                    "state": "unknown",
                    "anchors": ["AGENTS.md"],
                }
            ],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": ["bounded"],
            "reason": "bounded",
            "recovery_state": None,
        }
        self.assertEqual(corpus_engine.validate_output_result(result), result)
        malformed = copy.deepcopy(result)
        malformed["finding_classifications"][0]["anchors"] = [7]
        with self.assertRaisesRegex(ValueError, "schema|anchors|result"):
            corpus_engine.validate_output_result(malformed)
        malformed = copy.deepcopy(result)
        malformed["open_gates"] = ["unknown-gate"]
        with self.assertRaisesRegex(ValueError, "schema|gate|result"):
            corpus_engine.validate_output_result(malformed)

    def test_runtime_replays_action_permission_claim_and_persisted_authority(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo, _root = self._repo(raw)
            gate = self._gate(repo)
            descriptor = gate.descriptor()
            self.assertEqual(
                descriptor["authority_sha256"],
                gate._plan["authority_sha256"],
            )
            self.assertEqual(
                gate._binding["permission_digest"],
                live._permission_digest(gate._report, gate._authority, gate._plan),
            )
            self.assertEqual(
                gate._binding["claim_digest"],
                live._claim_digest(gate._plan),
            )

    def test_preflight_mismatch_writes_zero_claim_files(self) -> None:
        from evaluation.holdout import engine as holdout_engine

        with tempfile.TemporaryDirectory() as raw:
            repo, root = self._repo(raw)
            gate = self._gate(repo, gate="holdout", units=("wrong-pair",))
            output = Path(gate._plan["output"])
            before = sorted(path.name for path in root.iterdir())
            with mock.patch.object(
                holdout_engine, "resolve_output", return_value=output
            ), self.assertRaisesRegex(ValueError, "plan|invocation|units"):
                holdout_engine.run_holdouts(
                    candidate=repo,
                    public=repo.parent / "public",
                    output=output,
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout=300,
                    authorization=gate,
                )
            self.assertEqual(sorted(path.name for path in root.iterdir()), before)

    def test_template_expansion_and_phase_proof_are_thread_one_shot(self) -> None:
        parameters = inspect.signature(live._issue_phase_proof).parameters
        self.assertNotIn("argv", parameters)
        self.assertNotIn("cwd", parameters)
        self.assertNotIn("env", parameters)
        self.assertNotIn("timeout", parameters)
        self.assertTrue(hasattr(live, "_SPENT_PHASE_LOCK"))

    def test_holdout_pending_and_evidence_follow_adaptive_frontier(self) -> None:
        from evaluation.holdout import engine as holdout_engine

        pairs = ["pair-1", "pair-2", "pair-3"]
        self.assertEqual(holdout_engine.adaptive_frontier(pairs, []), ["pair-1"])
        self.assertEqual(
            holdout_engine.adaptive_frontier(pairs, ["equal"]), ["pair-2"]
        )
        self.assertEqual(
            holdout_engine.adaptive_frontier(pairs, ["better", "equal"]),
            ["pair-3"],
        )
        self.assertEqual(
            holdout_engine.adaptive_frontier(pairs, ["equal", "equal"]), []
        )
        self.assertEqual(
            holdout_engine.adaptive_frontier(pairs, ["regression"]), []
        )

    def test_output_creation_rejects_symlink_swap(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            victim = root / "victim"
            victim.mkdir()
            output = root / "output"
            corpus_engine.resolve_output_path(output, plugin=root / "plugin")
            output.symlink_to(victim, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink|output|changed"):
                corpus_engine.create_output_root(output)
            self.assertEqual(list(victim.iterdir()), [])

    def test_populated_replay_requires_repo(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        with self.assertRaisesRegex(ValueError, "repository|repo"):
            ledger_engine.replay_planned_lifecycle(lifecycle)

    def test_release_reanchor_precedes_evidence_without_reuse(self) -> None:
        lifecycle = self._lifecycle(certified=False)
        changed = copy.deepcopy(lifecycle)
        changed["source_anchor"]["source_commit"] = "f" * 40
        changed["source_anchor"]["source_tree"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "reanchor|evidence|reset|successor"):
            ledger_engine.validate_successor(lifecycle, changed)

    def test_agents_and_evaluation_readme_match_executable_generation6_behavior(
        self,
    ) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "evaluation" / "README.md").read_text(encoding="utf-8")
        for text in (agents, readme):
            self.assertIn("public-0.2", text)
            self.assertIn("PhaseProof", text)
            self.assertNotIn("G014 alone may replace", text)
        self.assertNotIn(
            "generation-6 live capability is unavailable until Batch3",
            corpus_engine.run_authorized.__code__.co_consts,
        )

    def test_structural_contract_is_semantic_and_hash_bound(self) -> None:
        contract_path = "evaluation/contracts-v6.json"
        inventory = engine_inventory(ROOT)
        categories = {item["path"]: item["category"] for item in inventory["entries"]}
        self.assertEqual(categories[contract_path], "semantic")
        self.assertEqual(categories["evaluation/core/schema.py"], "harness")
        self.assertIn(contract_path, CORPUS_SEMANTIC_PATHS)
        before = engine_paths_sha256(inventory, CORPUS_SEMANTIC_PATHS)
        with tempfile.TemporaryDirectory() as raw:
            clone = Path(raw) / "repo"
            shutil.copytree(ROOT / "evaluation", clone / "evaluation")
            path = clone / contract_path
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            changed = engine_inventory(clone)
        self.assertNotEqual(
            inventory["categories"]["semantic"], changed["categories"]["semantic"]
        )
        self.assertEqual(
            inventory["categories"]["harness"], changed["categories"]["harness"]
        )
        self.assertNotEqual(before, engine_paths_sha256(changed, CORPUS_SEMANTIC_PATHS))

    def test_structural_schema_validates_invocation_plan_and_snapshot_parity(
        self,
    ) -> None:
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        ledger = self._lifecycle(certified=False)
        profile = invocation_profile(
            model="gpt-5.6-sol", effort="high", timeout_seconds=300, arm="candidate"
        )
        for name, value in (
            ("invocation_profile", profile),
            ("gate_plan", ledger["planned_invocations"]["executor"]),
            ("snapshot", ledger["snapshot"]),
            ("planned_impact", ledger["planned_impact"]),
            ("source_anchor", ledger["source_anchor"]),
        ):
            with self.subTest(name=name):
                self.assertEqual(validate_named(contracts, name, value), value)

    def test_structural_schema_validates_evidence_and_ledger_parity(self) -> None:
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        ledger = self._lifecycle(certified=False)
        for record in ledger["accepted_evidence"].values():
            self.assertEqual(
                validate_named(contracts, "evidence_record", record), record
            )
        self.assertEqual(validate_named(contracts, "ledger", ledger), ledger)

    def test_ledger_recursively_rejects_nested_named_and_slot_record_drift(
        self,
    ) -> None:
        cases = (
            ("source", ("source_anchor", "source_commit"), "bad", "schema", False),
            (
                "impact",
                ("planned_impact", "initial_scope", "adaptive_policy_sha256"),
                "bad",
                "planned impact",
                False,
            ),
            (
                "plan",
                ("planned_invocations", "executor", "profile", "timeout_ms"),
                "bad",
                "persisted gate plan",
                False,
            ),
            (
                "cost",
                ("cost", "executor", "model_calls", "min"),
                "bad",
                "cost basis",
                False,
            ),
            (
                "evidence",
                ("accepted_evidence", "executor", "producer", "schema_version"),
                "bad",
                "evidence",
                True,
            ),
        )
        for label, path, value, error, populated in cases:
            invalid = self._lifecycle(certified=False) if populated else self._plan_only()
            cursor = invalid
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, error):
                validate_ledger(invalid)

    def test_structural_schema_leaves_cross_field_relations_in_python(self) -> None:
        from evaluation.core.identity import validate_invocation_profile
        from evaluation.core.impact import validate_snapshot
        from evaluation.core.schema import load_contracts, validate_named

        contracts = load_contracts(ROOT / "evaluation" / "contracts-v6.json")
        profile = invocation_profile(
            model="gpt-5.6-sol", effort="high", timeout_seconds=300, arm="candidate"
        )
        invalid_profile = copy.deepcopy(profile)
        invalid_profile["tools"]["event_item_types"] = []
        validate_named(contracts, "invocation_profile", invalid_profile)
        with self.assertRaisesRegex(ValueError, "invocation tool profile"):
            validate_invocation_profile(invalid_profile)

        snapshot = build_snapshot(ROOT)
        invalid_snapshot = copy.deepcopy(snapshot)
        invalid_snapshot["public_baseline"]["source_commit"] = "f" * 40
        validate_named(contracts, "snapshot", invalid_snapshot)
        with self.assertRaisesRegex(ValueError, "public-0.2 baseline"):
            validate_snapshot(invalid_snapshot)


if __name__ == "__main__":
    unittest.main()
