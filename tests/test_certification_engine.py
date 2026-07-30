from __future__ import annotations

import copy
import inspect
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from evaluation import live
from evaluation.core.identity import (
    canonical_sha256,
    engine_inventory,
    source_archive_identity,
)
from evaluation.core.impact import build_snapshot, plan_impact
from evaluation.core.ledger import (
    GATE_ORDER,
    append_record,
    derive_certified,
    derive_coverage,
    derive_failed,
    derive_freeze_eligibility,
    derive_pending,
    derive_receipt_tip,
    derive_status,
    validate_gate_plan,
    validate_gate_receipt,
    validate_ledger,
    validate_successor,
)
from evaluation.core.schema import CONTRACTS, validate_named
from evaluation.corpus import engine as corpus_engine
from evaluation.holdout import engine as holdout_engine


ROOT = Path(__file__).resolve().parents[1]
GENESIS = {
    "schema_version": 1,
    "candidate": None,
    "plans": [],
    "receipts": [],
}
ZERO_EFFECT_FIELDS = {
    "intents_created",
    "units_consumed",
    "fixtures_created",
    "outputs_created",
    "receipts_created",
    "workspaces_created",
    "subprocesses",
    "model_calls",
    "network_calls",
}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _prepare_repo(raw: str) -> Path:
    repo = Path(raw) / "repo"
    subprocess.run(
        ["git", "clone", "--quiet", str(ROOT), str(repo)],
        check=True,
    )
    _git(repo, "config", "user.name", "Batch 2 Test")
    _git(repo, "config", "user.email", "batch2@example.invalid")
    ledger = repo / "evaluation/results/current.json"
    ledger.write_text(
        json.dumps(GENESIS, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", "evaluation/results/current.json")
    _git(
        repo,
        "commit",
        "--quiet",
        "--allow-empty",
        "-m",
        "test: install clean genesis",
    )
    return repo


def _candidate(repo: Path, *, created_at: str = "2026-07-30T00:00:00Z") -> dict:
    identity = source_archive_identity(repo, "HEAD")
    snapshot = build_snapshot(repo)
    value = {
        "schema_version": 1,
        "record_type": "ReleaseCandidate",
        "source_commit": identity["source_commit"],
        "source_tree": identity["source_tree"],
        "package_artifact_sha256": identity["package"]["artifact_sha256"],
        "package_semantic_sha256": identity["package"]["semantic_sha256"],
        "engine_manifest_sha256": identity["engine_manifest_sha256"],
        "executor_role_sha256": identity["executor_role_sha256"],
        "public_baseline_sha256": canonical_sha256(snapshot["public_baseline"]),
        "snapshot_sha256": canonical_sha256(snapshot),
        "created_at": created_at,
    }
    value["candidate_sha256"] = canonical_sha256(value)
    return value


def _plan(
    candidate: dict,
    gate: str,
    output: Path,
    *,
    units: tuple[str, ...] = ("unit",),
    created_at: str = "2026-07-30T00:01:00Z",
    arm: str | None = None,
) -> dict:
    value = {
        "schema_version": 1,
        "record_type": "GatePlan",
        "candidate_sha256": candidate["candidate_sha256"],
        "gate": gate,
        "created_at": created_at,
        "profile": {
            "argv": [
                "python3",
                "-m",
                "evaluation.cli",
                gate,
                "--unit",
                "{unit}",
            ],
            "cwd": str(ROOT),
            "env": {},
            "timeout_ms": 300000,
            "model": "gpt-5.6-sol",
            "effort": "high",
            "arm": arm or ("blinded-pair" if gate == "holdout" else "candidate"),
        },
        "cost_ceiling": {
            "model_calls": 10,
            "uncached_input_tokens": 1_000_000,
            "output_tokens": 100_000,
            "wall_milliseconds": 1_000_000,
        },
        "units": sorted(units),
        "resource_digests": [canonical_sha256({"gate": gate})],
        "output": str(output.absolute()),
        "approval_request_sha256": canonical_sha256({"request": gate}),
        "approval_content_sha256": canonical_sha256({"approval": gate}),
    }
    value["plan_sha256"] = canonical_sha256(value)
    return value


def _receipt(
    candidate: dict,
    plan: dict,
    sequence: int,
    *,
    evidence_commit: str = "e" * 40,
    created_at: str = "2026-07-30T00:02:00Z",
    result: str = "succeeded",
    parent: str | None = None,
) -> dict:
    value = {
        "schema_version": 1,
        "record_type": "GateReceipt",
        "candidate_sha256": candidate["candidate_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "gate": plan["gate"],
        "sequence": sequence,
        "created_at": created_at,
        "evidence_commit": evidence_commit,
        "unit_results": [
            {
                "unit": unit,
                "status": result,
                "result_sha256": canonical_sha256(
                    {"gate": plan["gate"], "unit": unit, "result": result}
                ),
            }
            for unit in plan["units"]
        ],
        "result": result,
        "output_sha256": canonical_sha256({"gate": plan["gate"]}),
        "parent_receipt_sha256": parent,
    }
    value["receipt_sha256"] = canonical_sha256(value)
    return value


def _run_current_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "evaluation.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


class GenesisAndCliTests(unittest.TestCase):
    def test_active_ledger_is_fresh_three_family_genesis(self) -> None:
        active = json.loads(
            (ROOT / "evaluation/results/current.json").read_text(encoding="utf-8")
        )
        self.assertEqual(active, GENESIS)
        validate_ledger(active)
        self.assertEqual(derive_status(active), "refresh_required")
        self.assertEqual(derive_pending(active)["gates"], list(GATE_ORDER))

    def test_real_cli_applies_current_source_to_isolated_repo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            record = Path(raw) / "candidate.json"
            record.write_text(json.dumps(candidate) + "\n", encoding="utf-8")
            completed = _run_current_cli(
                "apply",
                "--repo",
                str(repo),
                "--ledger",
                "evaluation/results/current.json",
                "--expected",
                canonical_sha256(GENESIS),
                "--record",
                str(record),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["record_type"], "ReleaseCandidate")
            current = json.loads(
                (repo / "evaluation/results/current.json").read_text(encoding="utf-8")
            )
            self.assertEqual(current["candidate"], candidate)

    def test_cli_refuses_stale_predecessor_without_an_ambiguous_retry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            record = Path(raw) / "candidate.json"
            record.write_text(json.dumps(candidate) + "\n", encoding="utf-8")
            command = (
                "apply",
                "--repo",
                str(repo),
                "--ledger",
                "evaluation/results/current.json",
                "--expected",
                "0" * 64,
                "--record",
                str(record),
            )
            completed = _run_current_cli(*command)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("stale ledger predecessor", completed.stderr)
            self.assertEqual(
                json.loads(
                    (repo / "evaluation/results/current.json").read_text(
                        encoding="utf-8"
                    )
                ),
                GENESIS,
            )

    def test_cli_refuses_manual_worktree_ledger_drift(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            record = Path(raw) / "candidate.json"
            record.write_text(json.dumps(candidate) + "\n", encoding="utf-8")
            ledger = repo / "evaluation/results/current.json"
            ledger.write_text(
                json.dumps({**GENESIS, "plans": [{}]}) + "\n",
                encoding="utf-8",
            )
            completed = _run_current_cli(
                "apply",
                "--repo",
                str(repo),
                "--ledger",
                "evaluation/results/current.json",
                "--expected",
                canonical_sha256(GENESIS),
                "--record",
                str(record),
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("differs from prior Git ledger", completed.stderr)

    def test_all_dry_runs_are_zero_effect(self) -> None:
        commands = (
            ("executor", "--dry-run"),
            ("corpus", "--calibrate", "--dry-run"),
            ("corpus", "--case", "subthreshold-control", "--dry-run"),
            ("holdout", "--dry-run"),
        )
        for command in commands:
            with self.subTest(command=command):
                completed = _run_current_cli(*command)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual(set(payload["effects"]), ZERO_EFFECT_FIELDS)
                self.assertTrue(all(value == 0 for value in payload["effects"].values()))
        calibration = json.loads(_run_current_cli(*commands[1]).stdout)
        self.assertTrue(calibration["calibrate"])
        self.assertEqual(calibration["cases"], ["subthreshold-control"])


class LedgerRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = tempfile.TemporaryDirectory()
        self.repo = _prepare_repo(self.raw.name)
        self.candidate = _candidate(self.repo)

    def tearDown(self) -> None:
        self.raw.cleanup()

    def test_only_three_release_record_families_are_persisted(self) -> None:
        ledger = append_record(GENESIS, self.candidate, repo=self.repo)
        plan = _plan(
            self.candidate,
            "calibration",
            Path(self.raw.name) / "effects",
            units=("subthreshold-control",),
        )
        ledger = append_record(ledger, plan, repo=self.repo)
        receipt = _receipt(self.candidate, plan, 0)
        ledger = append_record(ledger, receipt)
        self.assertEqual(
            {
                ledger["candidate"]["record_type"],
                ledger["plans"][0]["record_type"],
                ledger["receipts"][0]["record_type"],
            },
            {"ReleaseCandidate", "GatePlan", "GateReceipt"},
        )
        self.assertEqual(set(ledger), {"schema_version", "candidate", "plans", "receipts"})

    def test_candidate_is_git_reachable_and_archive_exact(self) -> None:
        ledger = append_record(GENESIS, self.candidate, repo=self.repo)
        validate_ledger(ledger, repo=self.repo)
        changed = copy.deepcopy(self.candidate)
        changed["source_tree"] = "f" * 40
        changed["candidate_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "candidate_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "Git archive"):
            append_record(GENESIS, changed, repo=self.repo)

    def test_plan_requires_exact_sorted_units_resources_and_seal(self) -> None:
        plan = _plan(
            self.candidate,
            "corpus",
            Path(self.raw.name) / "effects",
            units=("b", "a"),
        )
        validate_gate_plan(plan)
        for field, value in (
            ("units", ["b", "a"]),
            ("resource_digests", [plan["resource_digests"][0]] * 2),
        ):
            invalid = copy.deepcopy(plan)
            invalid[field] = value
            invalid["plan_sha256"] = canonical_sha256(
                {key: item for key, item in invalid.items() if key != "plan_sha256"}
            )
            with self.assertRaises(ValueError):
                validate_gate_plan(invalid)

    def test_receipt_binds_plan_units_and_parent_chain(self) -> None:
        plan = _plan(
            self.candidate,
            "corpus",
            Path(self.raw.name) / "effects",
            units=("a", "b"),
        )
        receipt = _receipt(self.candidate, plan, 0)
        validate_gate_receipt(receipt)
        invalid = copy.deepcopy(receipt)
        invalid["unit_results"] = invalid["unit_results"][:-1]
        invalid["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in invalid.items() if key != "receipt_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "units do not equal"):
            validate_ledger(
                {
                    "schema_version": 1,
                    "candidate": self.candidate,
                    "plans": [plan],
                    "receipts": [invalid],
                }
            )

    def test_successor_appends_exactly_one_record(self) -> None:
        candidate_only = append_record(GENESIS, self.candidate, repo=self.repo)
        plan = _plan(
            self.candidate,
            "calibration",
            Path(self.raw.name) / "effects",
            units=("subthreshold-control",),
        )
        planned = append_record(candidate_only, plan, repo=self.repo)
        validate_successor(candidate_only, planned, repo=self.repo)
        invalid = copy.deepcopy(planned)
        invalid["plans"].append(
            _plan(
                self.candidate,
                "corpus",
                Path(self.raw.name) / "corpus",
                units=tuple(build_snapshot(self.repo)["corpus"]["cases"]),
                created_at="2026-07-30T00:02:00Z",
            )
        )
        with self.assertRaisesRegex(ValueError, "append exactly once"):
            validate_successor(candidate_only, invalid, repo=self.repo)

    def test_receipts_follow_canonical_gate_and_strict_time_order(self) -> None:
        plans = [
            _plan(
                self.candidate,
                gate,
                Path(self.raw.name) / gate,
                created_at=f"2026-07-30T00:01:{index:02d}Z",
            )
            for index, gate in enumerate(GATE_ORDER)
        ]
        receipts = []
        parent = None
        for index, plan in enumerate(plans):
            receipt = _receipt(
                self.candidate,
                plan,
                index,
                created_at=f"2026-07-30T00:02:{index:02d}Z",
                parent=parent,
            )
            receipts.append(receipt)
            parent = receipt["receipt_sha256"]
        ledger = {
            "schema_version": 1,
            "candidate": self.candidate,
            "plans": plans,
            "receipts": receipts,
        }
        validate_ledger(ledger)
        reordered = copy.deepcopy(ledger)
        reordered["receipts"][0], reordered["receipts"][1] = (
            reordered["receipts"][1],
            reordered["receipts"][0],
        )
        with self.assertRaises(ValueError):
            validate_ledger(reordered)
        equal_time = copy.deepcopy(ledger)
        equal_time["receipts"][0]["created_at"] = self.candidate["created_at"]
        equal_time["receipts"][0]["receipt_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in equal_time["receipts"][0].items()
                if key != "receipt_sha256"
            }
        )
        with self.assertRaisesRegex(ValueError, "chronology"):
            validate_ledger(equal_time)

    def test_derived_state_has_no_cached_lifecycle_fields(self) -> None:
        plans = [
            _plan(self.candidate, gate, Path(self.raw.name) / gate)
            for gate in GATE_ORDER
        ]
        receipts = []
        parent = None
        for index, plan in enumerate(plans):
            receipt = _receipt(
                self.candidate,
                plan,
                index,
                created_at=f"2026-07-30T00:02:{index:02d}Z",
                parent=parent,
            )
            receipts.append(receipt)
            parent = receipt["receipt_sha256"]
        ledger = {
            "schema_version": 1,
            "candidate": self.candidate,
            "plans": plans,
            "receipts": receipts,
        }
        self.assertEqual(set(derive_coverage(ledger)), set(GATE_ORDER))
        self.assertEqual(derive_pending(ledger)["gates"], [])
        self.assertEqual(derive_receipt_tip(ledger), parent)
        self.assertFalse(derive_freeze_eligibility(ledger))
        self.assertFalse(derive_certified(ledger))
        self.assertEqual(derive_status(ledger), "refresh_required")
        self.assertEqual(derive_failed(ledger), [])

    def test_first_failed_receipt_blocks_certification(self) -> None:
        plan = _plan(
            self.candidate,
            "calibration",
            Path(self.raw.name) / "effects",
        )
        failed = _receipt(self.candidate, plan, 0, result="failed")
        ledger = {
            "schema_version": 1,
            "candidate": self.candidate,
            "plans": [plan],
            "receipts": [failed],
        }
        self.assertEqual(derive_failed(ledger), ["calibration"])
        self.assertFalse(derive_freeze_eligibility(ledger))
        self.assertEqual(derive_status(ledger), "refresh_required")


class EffectIntentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = tempfile.TemporaryDirectory()
        self.root = Path(self.raw.name)
        self.claims = self.root / "claims"
        self.claims.mkdir(mode=0o700)
        self.candidate = {"candidate_sha256": "a" * 64}

    def tearDown(self) -> None:
        self.raw.cleanup()

    def _intent(self, *, gate: str = "corpus", unit: str = "unit") -> dict:
        plan = _plan(
            self.candidate,
            gate,
            self.root / "effects",
            units=(unit,),
        )
        return live.build_effect_intent(plan, unit)

    def test_intent_exactly_expands_and_binds_one_unit(self) -> None:
        intent = self._intent()
        self.assertEqual(intent["unit"], "unit")
        self.assertEqual(Path(intent["output"]), self.root / "effects" / "unit")
        self.assertIn("unit", intent["invocation"]["argv"])
        live.validate_effect_intent(intent, unit="unit")
        changed = copy.deepcopy(intent)
        changed["unit"] = "other"
        with self.assertRaises(ValueError):
            live.validate_effect_intent(changed)

    def test_reservation_is_durable_one_shot_before_output(self) -> None:
        intent = self._intent()
        reservation = live.reserve_effect(intent, self.claims)
        self.assertTrue(Path(reservation["claim"]).is_file())
        output = Path(reservation["output"])
        self.assertTrue(output.is_dir())
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
        with self.assertRaisesRegex(ValueError, "absent"):
            live.reserve_effect(intent, self.claims)

    def test_reservation_refuses_symlink_and_path_drift(self) -> None:
        intent = self._intent()
        target = self.root / "target"
        target.mkdir(mode=0o700)
        (self.root / "effects").symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "private real directory"):
            live.reserve_effect(intent, self.claims)
        self.assertEqual(list(self.claims.iterdir()), [])

    def test_result_is_immutable_bound_and_cost_checked(self) -> None:
        intent = self._intent()
        live.reserve_effect(intent, self.claims)
        result = {
            "schema_version": 1,
            "intent_digest": intent["intent_digest"],
            "unit": intent["unit"],
            "status": "succeeded",
            "output_sha256": canonical_sha256({"output": "ok"}),
            "usage": {
                "model_calls": 1,
                "uncached_input_tokens": 10,
                "output_tokens": 2,
                "wall_milliseconds": 20,
            },
        }
        result["result_sha256"] = canonical_sha256(result)
        live.write_effect_result(intent, self.claims, result)
        with self.assertRaises(FileExistsError):
            live.write_effect_result(intent, self.claims, result)
        excessive = copy.deepcopy(result)
        excessive["usage"]["model_calls"] = 11
        excessive["result_sha256"] = canonical_sha256(
            {key: value for key, value in excessive.items() if key != "result_sha256"}
        )
        (Path(intent["output"]) / "result.json").unlink()
        with self.assertRaisesRegex(ValueError, "cost ceiling"):
            live.write_effect_result(intent, self.claims, excessive)

    def test_corpus_rejects_invalid_intent_before_fixture_or_output(self) -> None:
        case = corpus_engine.load_cases()["subthreshold-control"]
        output = self.root / "raw"
        with mock.patch.object(corpus_engine, "build_fixture") as fixture:
            with self.assertRaisesRegex(ValueError, "EffectIntent"):
                corpus_engine.evaluate_case(
                    case,
                    plugin=ROOT,
                    output=output,
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout=300,
                    arm="candidate",
                    effect_intent={},
                )
        fixture.assert_not_called()
        self.assertFalse(output.exists())

    def test_holdout_rejects_invalid_intent_before_mapping(self) -> None:
        pair = holdout_engine.load_manifest()["pairs"][0]
        with mock.patch.object(holdout_engine, "seal_mapping") as mapping:
            with self.assertRaisesRegex(ValueError, "EffectIntent"):
                holdout_engine.run_pair(
                    pair,
                    candidate=ROOT,
                    public=ROOT,
                    output=self.root,
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout=300,
                    effect_intent={},
                )
        mapping.assert_not_called()

    def test_authorized_entrypoints_accept_only_intents_and_claim_root(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(corpus_engine.run_authorized).parameters),
            ("args", "effect_intents", "claim_root"),
        )
        self.assertEqual(
            tuple(inspect.signature(holdout_engine.run_authorized).parameters),
            ("args", "effect_intents", "claim_root"),
        )


class ContractProtocolAndImpactTests(unittest.TestCase):
    def test_contract_contains_only_clean_release_record_schemas(self) -> None:
        schemas = CONTRACTS["schemas"]
        for required in (
            "release_candidate",
            "gate_plan",
            "gate_receipt",
            "ledger",
        ):
            self.assertIn(required, schemas)
        serialized = json.dumps(CONTRACTS, sort_keys=True)
        for forbidden in (
            "source_anchor",
            "planned_invocations",
            "accepted_evidence",
            "receipt_head",
            "executor_pilot",
            "focused_hardening",
        ):
            self.assertNotIn(forbidden, serialized)
        validate_named(CONTRACTS, "ledger", GENESIS)

    def test_protocol_rejects_removed_phase_review_and_gate_values(self) -> None:
        from evaluation.protocol import validate_result

        phases = CONTRACTS["schemas"]["output_result"]["properties"][
            "recovery_state"
        ]["properties"]["milestone_phase"]["enum"]
        self.assertEqual(
            phases,
            ["working", "candidate_frozen", "exact_final", "closed"],
        )
        self.assertLessEqual(len(phases), 4)
        base = {
            "decision": "complete",
            "qualifies": True,
            "execplan_condition": "usable",
            "protocol_may_product_write": False,
            "protocol_review_mode": "none",
            "protocol_may_complete": True,
            "finding_classifications": [],
            "blocker_classifications": [],
            "open_gates": [],
            "evidence": ["fixture"],
            "reason": "fixture",
            "recovery_state": {
                "baseline_revision": "a" * 40,
                "baseline_tree": "b" * 40,
                "current_revision": "c" * 40,
                "current_tree": "d" * 40,
                "writer": "Root",
                "milestone_phase": "working",
                "next_action": "none",
                "pending_gates": [],
                "tests": {
                    "passed": 1,
                    "failed": 0,
                    "accepted_failures": 0,
                    "marker_ids": [],
                },
                "worktree": "clean",
                "live_agents": [],
                "marker_ids": [],
            },
        }
        validate_result(base)
        for path, value in (
            (("protocol_review_mode",), "focused_hardening"),
            (("recovery_state", "milestone_phase"), "implementation"),
            (("recovery_state", "next_action"), "focused_review"),
            (("recovery_state", "pending_gates"), ["boundary_repair"]),
        ):
            invalid = copy.deepcopy(base)
            cursor = invalid
            for component in path[:-1]:
                cursor = cursor[component]
            cursor[path[-1]] = value
            with self.assertRaises(ValueError):
                validate_result(invalid)

    def test_engine_inventory_has_no_archived_semantic_fallback(self) -> None:
        inventory = engine_inventory(ROOT)
        paths = {entry["path"] for entry in inventory["entries"]}
        self.assertIn("evaluation/protocol.py", paths)
        retired_prefix = "/".join(("evaluation", "semantic")) + "/"
        self.assertFalse(any(path.startswith(retired_prefix) for path in paths))

    def test_genesis_impact_requires_full_fresh_gate_set(self) -> None:
        snapshot = build_snapshot(ROOT)
        pending = {
            "gates": list(GATE_ORDER),
            "corpus_cases": sorted(snapshot["corpus"]["cases"]),
            "holdout_pairs": sorted(snapshot["holdout"]["pairs"]),
        }
        impact = plan_impact(snapshot, snapshot, pending=pending)
        self.assertEqual(impact["gates"], list(GATE_ORDER))
        self.assertIn("generation_6_genesis", impact["reasons"])
        self.assertIsNone(impact["live_calls"])
        self.assertIsNone(impact["cost"])


class FalseGreenBoundaryTests(unittest.TestCase):
    def test_empty_gate_plans_and_receipts_cannot_certify(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            plans = []
            receipts = []
            parent = None
            for index, gate in enumerate(GATE_ORDER):
                plan = _plan(
                    candidate,
                    gate,
                    Path(raw) / gate,
                    units=(),
                    created_at=f"2026-07-30T00:01:{index:02d}Z",
                )
                plan["resource_digests"] = []
                plan["plan_sha256"] = canonical_sha256(
                    {
                        key: value
                        for key, value in plan.items()
                        if key != "plan_sha256"
                    }
                )
                plans.append(plan)
                receipt = _receipt(
                    candidate,
                    plan,
                    index,
                    created_at=f"2026-07-30T00:02:{index:02d}Z",
                    parent=parent,
                )
                receipt["output_sha256"] = None
                receipt["receipt_sha256"] = canonical_sha256(
                    {
                        key: value
                        for key, value in receipt.items()
                        if key != "receipt_sha256"
                    }
                )
                receipts.append(receipt)
                parent = receipt["receipt_sha256"]
            ledger = {
                "schema_version": 1,
                "candidate": candidate,
                "plans": plans,
                "receipts": receipts,
            }
            with self.assertRaises(ValueError):
                validate_ledger(ledger)

    def test_gate_plan_units_are_safe_single_path_components(self) -> None:
        candidate = {"candidate_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as raw:
            for unit in (
                "/tmp/escaped-unit",
                "nested/unit",
                r"nested\unit",
                ".",
                "..",
                " unit",
                "unit ",
                "unit\nalias",
                "unit\x00alias",
            ):
                with self.subTest(unit=repr(unit)):
                    plan = _plan(
                        candidate,
                        "corpus",
                        Path(raw) / "effects",
                        units=(unit,),
                    )
                    with self.assertRaises(ValueError):
                        validate_gate_plan(plan)

    def test_success_receipt_requires_units_and_output_digest(self) -> None:
        candidate = {"candidate_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as raw:
            plan = _plan(candidate, "receipt", Path(raw) / "effects")
            receipt = _receipt(
                candidate,
                plan,
                0,
                created_at="2026-07-30T00:02:00Z",
            )
            for field, value in (
                ("unit_results", []),
                ("output_sha256", None),
            ):
                invalid = copy.deepcopy(receipt)
                invalid[field] = value
                invalid["receipt_sha256"] = canonical_sha256(
                    {
                        key: item
                        for key, item in invalid.items()
                        if key != "receipt_sha256"
                    }
                )
                with self.subTest(field=field), self.assertRaises(ValueError):
                    validate_gate_receipt(invalid)

    def test_candidate_binds_exact_snapshot_public_and_current_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            forged = copy.deepcopy(candidate)
            forged["public_baseline_sha256"] = "0" * 64
            forged["snapshot_sha256"] = "1" * 64
            forged["candidate_sha256"] = canonical_sha256(
                {
                    key: value
                    for key, value in forged.items()
                    if key != "candidate_sha256"
                }
            )
            from evaluation.core.ledger import validate_release_candidate

            with self.assertRaises(ValueError):
                validate_release_candidate(forged, repo=repo)
            (repo / "README.md").write_text("changed after candidate\n", encoding="utf-8")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "--quiet", "-m", "test: change candidate input")
            with self.assertRaises(ValueError):
                validate_release_candidate(candidate, repo=repo)

    def test_repo_ledger_binds_full_model_scopes_and_settings(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            snapshot = build_snapshot(repo)
            calibration = _plan(
                candidate,
                "calibration",
                Path(raw) / "calibration",
                units=("subthreshold-control",),
            )
            corpus = _plan(
                candidate,
                "corpus",
                Path(raw) / "corpus",
                units=tuple(snapshot["corpus"]["cases"]),
                created_at="2026-07-30T00:01:01Z",
            )
            holdout = _plan(
                candidate,
                "holdout",
                Path(raw) / "holdout",
                units=tuple(snapshot["holdout"]["pairs"]),
                created_at="2026-07-30T00:01:02Z",
            )
            exact = {
                "schema_version": 1,
                "candidate": candidate,
                "plans": [calibration, corpus, holdout],
                "receipts": [],
            }
            validate_ledger(exact, repo=repo)
            mutations = (
                ("calibration scope", 0, ["clean-qualifying-control"]),
                ("corpus scope", 1, ["subthreshold-control"]),
                ("holdout scope", 2, ["local-documentation-control"]),
                ("model", 1, "other-model"),
                ("effort", 1, "low"),
                ("timeout", 1, 1),
                ("arm", 2, "candidate"),
            )
            for label, index, value in mutations:
                invalid = copy.deepcopy(exact)
                plan = invalid["plans"][index]
                if label.endswith("scope"):
                    plan["units"] = value
                else:
                    field = "timeout_ms" if label == "timeout" else label
                    plan["profile"][field] = value
                plan["plan_sha256"] = canonical_sha256(
                    {
                        key: item
                        for key, item in plan.items()
                        if key != "plan_sha256"
                    }
                )
                with self.subTest(label=label), self.assertRaises(ValueError):
                    validate_ledger(invalid, repo=repo)

    def test_repo_less_certification_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            plans = [
                _plan(
                    candidate,
                    gate,
                    Path(raw) / gate,
                    created_at=f"2026-07-30T00:01:{index:02d}Z",
                )
                for index, gate in enumerate(GATE_ORDER)
            ]
            receipts = []
            parent = None
            for index, plan in enumerate(plans):
                receipt = _receipt(
                    candidate,
                    plan,
                    index,
                    created_at=f"2026-07-30T00:02:{index:02d}Z",
                    parent=parent,
                )
                receipts.append(receipt)
                parent = receipt["receipt_sha256"]
            ledger = {
                "schema_version": 1,
                "candidate": candidate,
                "plans": plans,
                "receipts": receipts,
            }
            self.assertFalse(derive_certified(ledger))

    def test_cli_refuses_unpersisted_intent_before_runner(self) -> None:
        from argparse import Namespace
        from evaluation import cli

        candidate = {"candidate_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as raw:
            plan = _plan(
                candidate,
                "corpus",
                Path(raw) / "effects",
                units=("subthreshold-control",),
            )
            intent = live.build_effect_intent(plan, "subthreshold-control")
            args = Namespace(command="corpus", plugin=ROOT)
            with mock.patch.object(corpus_engine, "run_authorized") as runner:
                with self.assertRaises(ValueError):
                    cli.run_authorized(
                        args,
                        {"subthreshold-control": intent},
                        Path(raw),
                    )
            runner.assert_not_called()

    def test_load_ledger_refuses_symlink_and_parent_alias(self) -> None:
        from evaluation.core.ledger import load_ledger

        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            ledger = repo / "evaluation/results/current.json"
            target = repo / "evaluation/results/real-current.json"
            ledger.rename(target)
            ledger.symlink_to(target.name)
            with self.assertRaisesRegex(ValueError, "symlink|alias|drift"):
                load_ledger(ledger)
            alias = Path(raw) / "repo-alias"
            alias.symlink_to(repo, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink|alias|drift"):
                load_ledger(alias / "evaluation/results/real-current.json")


class AdaptiveHoldoutReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = tempfile.TemporaryDirectory()
        cls.repo = _prepare_repo(cls.raw.name)
        cls.candidate = _candidate(cls.repo)
        cls.snapshot = build_snapshot(cls.repo)
        cls.plan = _plan(
            cls.candidate,
            "holdout",
            Path(cls.raw.name) / "holdout",
            units=tuple(cls.snapshot["holdout"]["pairs"]),
            arm="blinded-pair",
        )
        manifest = holdout_engine.load_manifest(
            cls.repo / "evaluation/holdouts/manifest.json"
        )
        cls.execution_order = [pair["id"] for pair in manifest["pairs"]]
        _git(
            cls.repo,
            "commit",
            "--quiet",
            "--allow-empty",
            "-m",
            "test: add holdout evidence",
        )
        cls.evidence_commit = _git(cls.repo, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.raw.cleanup()

    def _receipt_for(
        self,
        plan: dict,
        units: list[str],
        *,
        result: str,
    ) -> dict:
        receipt = _receipt(
            self.candidate,
            plan,
            0,
            evidence_commit=self.evidence_commit,
            result=result,
        )
        selected = set(units)
        receipt["unit_results"] = [
            item for item in receipt["unit_results"] if item["unit"] in selected
        ]
        receipt["receipt_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in receipt.items()
                if key != "receipt_sha256"
            }
        )
        return receipt

    def _ledger(self, plan: dict, receipt: dict) -> dict:
        return {
            "schema_version": 1,
            "candidate": self.candidate,
            "plans": [plan],
            "receipts": [receipt],
        }

    def test_one_result_failed_holdout_prefix_is_valid(self) -> None:
        receipt = self._receipt_for(
            self.plan,
            self.execution_order[:1],
            result="failed",
        )
        validate_ledger(self._ledger(self.plan, receipt), repo=self.repo)

    def test_two_result_successful_holdout_prefix_is_valid(self) -> None:
        receipt = self._receipt_for(
            self.plan,
            self.execution_order[:2],
            result="succeeded",
        )
        validate_ledger(self._ledger(self.plan, receipt), repo=self.repo)

    def test_one_result_successful_holdout_prefix_is_invalid(self) -> None:
        receipt = self._receipt_for(
            self.plan,
            self.execution_order[:1],
            result="succeeded",
        )
        with self.assertRaises(ValueError):
            validate_ledger(self._ledger(self.plan, receipt), repo=self.repo)

    def test_holdout_prefix_cannot_skip_mandatory_second_pair(self) -> None:
        receipt = self._receipt_for(
            self.plan,
            [self.execution_order[0], self.execution_order[2]],
            result="succeeded",
        )
        with self.assertRaises(ValueError):
            validate_ledger(self._ledger(self.plan, receipt), repo=self.repo)

    def test_all_three_successful_holdout_results_are_valid(self) -> None:
        receipt = self._receipt_for(
            self.plan,
            self.execution_order,
            result="succeeded",
        )
        validate_ledger(self._ledger(self.plan, receipt), repo=self.repo)

    def test_every_non_holdout_partial_receipt_is_invalid(self) -> None:
        for gate in (item for item in GATE_ORDER if item != "holdout"):
            if gate == "calibration":
                units = ("subthreshold-control",)
            elif gate == "corpus":
                units = tuple(self.snapshot["corpus"]["cases"])
            else:
                units = ("unit-a", "unit-b")
            plan = _plan(
                self.candidate,
                gate,
                Path(self.raw.name) / gate,
                units=units,
            )
            receipt = self._receipt_for(
                plan,
                list(plan["units"][:-1]),
                result="succeeded",
            )
            with self.subTest(gate=gate), self.assertRaises(ValueError):
                validate_ledger(self._ledger(plan, receipt), repo=self.repo)


class Batch3IdentityContractionTests(unittest.TestCase):
    def test_evaluator_identity_is_one_closed_bundle(self) -> None:
        inventory = engine_inventory(ROOT)
        self.assertEqual(
            set(inventory),
            {"schema_version", "entries", "manifest_sha256"},
        )
        self.assertTrue(inventory["entries"])
        self.assertTrue(
            all(
                set(entry) == {"path", "bytes", "sha256"}
                for entry in inventory["entries"]
            )
        )
        snapshot = build_snapshot(ROOT)
        self.assertEqual(
            set(snapshot["settings"]),
            {"model", "effort", "timeout_seconds"},
        )
        self.assertEqual(
            snapshot["engine"],
            {"manifest_sha256": inventory["manifest_sha256"]},
        )

    def test_evaluator_bundle_change_requires_every_live_quality_gate(self) -> None:
        baseline = build_snapshot(ROOT)
        current = copy.deepcopy(baseline)
        current["engine"]["manifest_sha256"] = "f" * 64
        impact = plan_impact(baseline, current)
        self.assertEqual(
            impact["gates"],
            ["corpus", "holdout", "receipt"],
        )
        self.assertEqual(
            impact["corpus_cases"],
            sorted(current["corpus"]["cases"]),
        )
        self.assertEqual(
            impact["holdout_pairs"],
            sorted(current["holdout"]["pairs"]),
        )

    def test_live_codex_identity_has_only_version_and_content_digest(self) -> None:
        from evaluation.core.identity import codex_identity

        identity = codex_identity()
        self.assertEqual(set(identity), {"version", "sha256"})
        self.assertRegex(identity["sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(identity["version"])

    def test_unknown_python_and_json_evaluator_inputs_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            for relative in (
                "evaluation/unexpected.py",
                "evaluation/unexpected.json",
            ):
                path = repo / relative
                path.write_text("{}\n", encoding="utf-8")
                with self.subTest(relative=relative), self.assertRaises(ValueError):
                    engine_inventory(repo)
                path.unlink()

    def test_real_evaluator_file_change_invalidates_every_quality_unit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            baseline = build_snapshot(repo)
            protocol = repo / "evaluation/protocol.py"
            protocol.write_text(
                protocol.read_text(encoding="utf-8") + "\n# evaluator change\n",
                encoding="utf-8",
            )
            current = build_snapshot(repo)
            impact = plan_impact(baseline, current)
            self.assertEqual(
                impact["gates"],
                ["corpus", "holdout", "receipt"],
            )
            self.assertEqual(
                impact["corpus_cases"],
                sorted(current["corpus"]["cases"]),
            )
            self.assertEqual(
                impact["holdout_pairs"],
                sorted(current["holdout"]["pairs"]),
            )


if __name__ == "__main__":
    unittest.main()
