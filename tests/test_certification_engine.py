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
    "launches_created",
    "actions_consumed",
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
    value = {
        "schema_version": 1,
        "record_type": "ReleaseCandidate",
        "source_commit": identity["source_commit"],
        "source_tree": identity["source_tree"],
        "package_artifact_sha256": identity["package"]["artifact_sha256"],
        "package_semantic_sha256": identity["package"]["semantic_sha256"],
        "executor_role_sha256": identity["executor_role_sha256"],
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
    repo: Path = ROOT,
) -> dict:
    value = {
        "schema_version": 1,
        "record_type": "GatePlan",
        "candidate_sha256": candidate["candidate_sha256"],
        "snapshot_sha256": canonical_sha256(build_snapshot(repo)),
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
    def test_active_ledger_has_exact_generation7_candidate(self) -> None:
        active = json.loads(
            (ROOT / "evaluation/results/current.json").read_text(encoding="utf-8")
        )
        expected_candidate = {
            "candidate_sha256": "908a926287fa01cb8e4b4cf591b2a90d108a0b9bfe3d39affa7f39e9908f187e",
            "created_at": "2026-07-30T18:19:51Z",
            "executor_role_sha256": "f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da",
            "package_artifact_sha256": "bbc82a07445104820fb4e2108dde252fcce1883136e34e5ef1733eb3984b8b33",
            "package_semantic_sha256": "9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a",
            "record_type": "ReleaseCandidate",
            "schema_version": 1,
            "source_commit": "3a8e7d7ed7697c53d4b9c574a5fec1031ca0cc19",
            "source_tree": "799199be73b0d995fda2d52ee8b50bd92692efe1",
        }
        self.assertEqual(
            active,
            {
                "schema_version": 1,
                "candidate": expected_candidate,
                "plans": [],
                "receipts": [],
            },
        )
        validate_ledger(active, repo=ROOT)
        self.assertEqual(derive_status(active), "refresh_required")
        self.assertEqual(derive_pending(active)["gates"], list(GATE_ORDER))
        self.assertEqual(derive_coverage(active), {})
        self.assertEqual(derive_failed(active), [])
        self.assertFalse(derive_certified(active, repo=ROOT))

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
            repo=self.repo,
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
            repo=self.repo,
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
                repo=self.repo,
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


class LaunchGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = tempfile.TemporaryDirectory()
        self.root = Path(self.raw.name)
        self.claims = self.root / "claims"
        self.claims.mkdir(mode=0o700)
        self.candidate = {"candidate_sha256": "a" * 64}

    def tearDown(self) -> None:
        self.raw.cleanup()

    def _launch(
        self,
        *,
        gate: str = "corpus",
        unit: str = "unit",
        output: str = "effects",
        infrastructure: str | None = None,
    ) -> dict:
        plan = _plan(
            self.candidate,
            gate,
            self.root / output,
            units=(unit,),
        )
        return live.build_launch(
            plan,
            unit,
            infrastructure_generation=infrastructure,
        )

    def test_launch_exactly_expands_and_binds_one_unit(self) -> None:
        launch = self._launch()
        self.assertEqual(launch["unit"], "unit")
        self.assertEqual(Path(launch["output"]), self.root / "effects" / "unit")
        self.assertIn("unit", launch["invocation"]["argv"])
        self.assertRegex(launch["action_key"], r"^[0-9a-f]{64}$")
        live.validate_launch(launch, unit="unit")
        changed = copy.deepcopy(launch)
        changed["unit"] = "other"
        with self.assertRaises(ValueError):
            live.validate_launch(changed)

    def test_reservation_is_durable_one_shot_before_output(self) -> None:
        launch = self._launch(infrastructure="1" * 64)
        reservation = live.reserve_launch(launch, self.claims)
        self.assertTrue(Path(reservation["claim"]).is_file())
        output = Path(reservation["output"])
        self.assertTrue(output.is_dir())
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
        with self.assertRaisesRegex(ValueError, "absent"):
            live.reserve_launch(launch, self.claims)

        no_effect = {
            "schema_generation": 7,
            "action_key": launch["action_key"],
            "launch_key": launch["launch_key"],
            "unit": launch["unit"],
            "status": "failed",
            "effect": "no_effect",
            "output_sha256": None,
            "usage": {
                "model_calls": 0,
                "uncached_input_tokens": 0,
                "output_tokens": 0,
                "wall_milliseconds": 0,
            },
        }
        no_effect["result_sha256"] = canonical_sha256(no_effect)
        live.write_launch_result(launch, self.claims, no_effect)
        replacement = self._launch(
            output="replacement",
            infrastructure="2" * 64,
        )
        self.assertEqual(replacement["action_key"], launch["action_key"])
        live.reserve_launch(replacement, self.claims)
        exhausted = self._launch(
            output="exhausted",
            infrastructure="3" * 64,
        )
        with self.assertRaisesRegex(ValueError, "exhausted"):
            live.reserve_launch(exhausted, self.claims)

    def test_reservation_refuses_symlink_and_path_drift(self) -> None:
        launch = self._launch()
        target = self.root / "target"
        target.mkdir(mode=0o700)
        (self.root / "effects").symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "private real directory"):
            live.reserve_launch(launch, self.claims)
        self.assertFalse(
            any(path.name.startswith("launch-") for path in self.claims.iterdir())
        )

    def test_result_is_immutable_bound_and_cost_checked(self) -> None:
        launch = self._launch()
        live.reserve_launch(launch, self.claims)
        live.consume_action(launch, self.claims)
        result = {
            "schema_generation": 7,
            "action_key": launch["action_key"],
            "launch_key": launch["launch_key"],
            "unit": launch["unit"],
            "status": "succeeded",
            "effect": "provider_reached",
            "output_sha256": canonical_sha256({"output": "ok"}),
            "usage": {
                "model_calls": 1,
                "uncached_input_tokens": 10,
                "output_tokens": 2,
                "wall_milliseconds": 20,
            },
        }
        result["result_sha256"] = canonical_sha256(result)
        live.write_launch_result(launch, self.claims, result)
        with self.assertRaises(FileExistsError):
            live.write_launch_result(launch, self.claims, result)
        excessive = copy.deepcopy(result)
        excessive["usage"]["model_calls"] = 11
        excessive["result_sha256"] = canonical_sha256(
            {key: value for key, value in excessive.items() if key != "result_sha256"}
        )
        (Path(launch["output"]) / "result.json").unlink()
        with self.assertRaisesRegex(ValueError, "cost ceiling"):
            live.write_launch_result(launch, self.claims, excessive)

    def test_corpus_rejects_invalid_launch_before_fixture_or_output(self) -> None:
        case = corpus_engine.load_cases()["subthreshold-control"]
        output = self.root / "raw"
        with mock.patch.object(corpus_engine, "build_fixture") as fixture:
            with self.assertRaisesRegex(ValueError, "launch"):
                corpus_engine.evaluate_case(
                    case,
                    plugin=ROOT,
                    output=output,
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout=300,
                    arm="candidate",
                    launch={},
                    claim_root=self.claims,
                )
        fixture.assert_not_called()
        self.assertFalse(output.exists())

    def test_holdout_rejects_invalid_launch_before_mapping(self) -> None:
        pair = holdout_engine.load_manifest()["pairs"][0]
        with mock.patch.object(holdout_engine, "seal_mapping") as mapping:
            with self.assertRaisesRegex(ValueError, "launch"):
                holdout_engine.run_pair(
                    pair,
                    candidate=ROOT,
                    public=ROOT,
                    output=self.root,
                    model="gpt-5.6-sol",
                    effort="high",
                    timeout=300,
                    launch={},
                    claim_root=self.claims,
                )
        mapping.assert_not_called()

    def test_authorized_entrypoints_accept_only_launches_and_claim_root(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(corpus_engine.run_authorized).parameters),
            ("args", "launches", "claim_root"),
        )
        self.assertEqual(
            tuple(inspect.signature(holdout_engine.run_authorized).parameters),
            ("args", "launches", "claim_root"),
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
        from evaluation.semantic import SemanticError, parse_model_observation

        phases = CONTRACTS["schemas"]["recovery"]["properties"][
            "milestone_phase"
        ]["enum"]
        self.assertEqual(
            phases,
            ["working", "candidate_frozen", "exact_final", "closed"],
        )
        self.assertLessEqual(len(phases), 4)
        base = {
            "qualifies": True,
            "execplan_condition": "usable",
            "findings": [],
            "open_gates": [],
            "evidence": ["fixture"],
            "reason": "fixture",
            "recovery": {
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
        parse_model_observation(base)
        for path, value in (
            (("protocol_review_mode",), "focused_hardening"),
            (("recovery", "milestone_phase"), "implementation"),
            (("recovery", "next_action"), "focused_review"),
            (("recovery", "pending_gates"), ["boundary_repair"]),
        ):
            invalid = copy.deepcopy(base)
            cursor = invalid
            for component in path[:-1]:
                cursor = cursor[component]
            cursor[path[-1]] = value
            with self.assertRaises(SemanticError):
                parse_model_observation(invalid)

    def test_engine_inventory_has_no_archived_semantic_fallback(self) -> None:
        inventory = engine_inventory(ROOT)
        paths = {entry["path"] for entry in inventory["entries"]}
        self.assertNotIn("evaluation/protocol.py", paths)
        self.assertEqual(
            {
                path
                for path in paths
                if path.startswith("evaluation/semantic/")
            },
            {
                "evaluation/semantic/__init__.py",
                "evaluation/semantic/codec.py",
                "evaluation/semantic/model.py",
                "evaluation/semantic/reducer.py",
                "evaluation/semantic/replay.py",
            },
        )

    def test_genesis_impact_requires_full_fresh_gate_set(self) -> None:
        snapshot = build_snapshot(ROOT)
        pending = {
            "gates": list(GATE_ORDER),
            "corpus_cases": sorted(snapshot["corpus"]["cases"]),
            "holdout_pairs": sorted(snapshot["holdout"]["pairs"]),
        }
        impact = plan_impact(snapshot, snapshot, pending=pending)
        self.assertEqual(impact["gates"], list(GATE_ORDER))
        self.assertIn("generation_7_genesis", impact["reasons"])
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

    def test_evaluator_only_drift_preserves_candidate_but_invalidates_plan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = _prepare_repo(raw)
            candidate = _candidate(repo)
            plan = _plan(
                candidate,
                "calibration",
                Path(raw) / "calibration",
                units=("subthreshold-control",),
                repo=repo,
            )
            from evaluation.core.ledger import validate_release_candidate

            exact = {
                "schema_version": 1,
                "candidate": candidate,
                "plans": [plan],
                "receipts": [],
            }
            validate_ledger(exact, repo=repo)
            reducer = repo / "evaluation/semantic/reducer.py"
            reducer.write_text(
                reducer.read_text(encoding="utf-8") + "\n# evaluator-only drift\n",
                encoding="utf-8",
            )
            _git(repo, "add", "evaluation/semantic/reducer.py")
            _git(repo, "commit", "--quiet", "-m", "test: change evaluator only")
            validate_release_candidate(candidate, repo=repo)
            with self.assertRaises(ValueError):
                validate_ledger(exact, repo=repo)

            refreshed = _plan(
                candidate,
                "calibration",
                Path(raw) / "refreshed-calibration",
                units=("subthreshold-control",),
                repo=repo,
            )
            validate_ledger(
                {**exact, "plans": [refreshed]},
                repo=repo,
            )

    def test_product_package_or_executor_role_drift_invalidates_candidate(self) -> None:
        from evaluation.core.ledger import validate_release_candidate

        for relative in ("README.md", "evaluation/executor-role.json"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as raw:
                repo = _prepare_repo(raw)
                candidate = _candidate(repo)
                path = repo / relative
                if relative == "README.md":
                    path.write_text(
                        path.read_text(encoding="utf-8") + "\nproduct drift\n",
                        encoding="utf-8",
                    )
                else:
                    role = json.loads(path.read_text(encoding="utf-8"))
                    role["model"] = "other-model"
                    path.write_text(
                        json.dumps(role, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8",
                    )
                _git(repo, "add", relative)
                _git(repo, "commit", "--quiet", "-m", "test: product drift")
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
                repo=repo,
            )
            corpus = _plan(
                candidate,
                "corpus",
                Path(raw) / "corpus",
                units=tuple(snapshot["corpus"]["cases"]),
                created_at="2026-07-30T00:01:01Z",
                repo=repo,
            )
            holdout = _plan(
                candidate,
                "holdout",
                Path(raw) / "holdout",
                units=tuple(snapshot["holdout"]["pairs"]),
                created_at="2026-07-30T00:01:02Z",
                repo=repo,
            )
            exact = {
                "schema_version": 1,
                "candidate": candidate,
                "plans": [calibration, corpus, holdout],
                "receipts": [],
            }
            validate_ledger(exact, repo=repo)
            mutations = (
                ("snapshot", 0, "0" * 64),
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
            launch = live.build_launch(plan, "subthreshold-control")
            args = Namespace(command="corpus", plugin=ROOT)
            with mock.patch.object(corpus_engine, "run_authorized") as runner:
                with self.assertRaises(ValueError):
                    cli.run_authorized(
                        args,
                        {"subthreshold-control": launch},
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
            repo=cls.repo,
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
                repo=self.repo,
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
            reducer = repo / "evaluation/semantic/reducer.py"
            reducer.write_text(
                reducer.read_text(encoding="utf-8") + "\n# evaluator change\n",
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
