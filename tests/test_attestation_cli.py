from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from evaluation.host import attestation_from_raw
from evaluation.manifest import materialize_eval_spec
from evaluation.provider import (
    BEHAVIOR_DEVELOPER_INSTRUCTIONS, build_fixed_host_policy,
    host_contract_from_policy,
)
from evaluation.records import canonical_sha256
from evaluation.verify import exact_final_authority_proposal
from tests.attestation_fixtures import (
    HOST_CONTRACT, PROFILES, REVEALED_AT, REVIEW_BRIEF, ROOT, TOTAL_CAP, SHA,
    attest_all, bundle, passing_report, previous_product, product, reseal,
    write_json,
)
from tests.test_fixed_host_transaction_v2 import _synthetic_snapshot


class FreshProcessTests(unittest.TestCase):
    def _exact_request_fixture(self, temp: Path):
        (temp / "execution").mkdir(mode=0o700)
        snapshot, oracle = _synthetic_snapshot(temp)
        marker = temp / "provider-reached"
        binary = temp / "provider"
        binary.write_text(f"#!/bin/sh\ntouch {marker}\nexit 99\n", encoding="utf-8")
        binary.chmod(0o700)
        role = temp / "happycodex_executor.toml"
        role.write_text(
            'name = "happycodex_executor"\nmodel = "gpt-fake"\n'
            'model_reasoning_effort = "high"\ndeveloper_instructions = """\n'
            + BEHAVIOR_DEVELOPER_INSTRUCTIONS + '"""\n[features]\nplugins = false\n',
            encoding="utf-8",
        )
        role.chmod(0o600)
        role_sha = hashlib.sha256(role.read_bytes()).hexdigest()
        selected, baseline = product(role=role_sha), previous_product(role=role_sha)
        mapping = bundle()[3]
        mapping_path = temp / "mapping.json"; write_json(mapping_path, mapping); mapping_path.chmod(0o600)
        execution = temp / "reference-execution"; execution.mkdir(mode=0o700)
        for name in ("units", "raw", "attestations", "claims"):
            (execution / name).mkdir(mode=0o700)
        policy = build_fixed_host_policy(
            execution_root=execution, binary_path=binary,
            external_role_config_path=role, exact_final_source=snapshot,
            holdout_mapping_path=mapping_path, private_oracle_path=oracle,
            behavior_model="gpt-fake", behavior_effort="high",
        )
        contract = host_contract_from_policy(policy)
        previous = materialize_eval_spec(
            root=ROOT, candidate=selected, previous=baseline, profiles=PROFILES,
            total_cap=TOTAL_CAP, holdout_mapping=mapping,
            review_brief=REVIEW_BRIEF,
            host_contract={**contract, "exact_final_sha256": SHA["4"]},
        )
        records, raws = attest_all(selected, baseline, previous)
        prior = [record for record in records if record["unit_id"] != "exact-final"]
        values = {
            "product": selected, "previous-product": baseline,
            "previous-spec": previous, "profiles": PROFILES,
            "total-cap": TOTAL_CAP,
            "effect-cap": {**TOTAL_CAP, "model_calls": 1},
            "mapping": mapping, "review-brief": REVIEW_BRIEF,
        }
        paths = {}
        for name, value in values.items():
            paths[name] = temp / f"{name}.json"; write_json(paths[name], value)
        attestations, raw_paths = {}, {}
        for record in prior:
            unit_id = record["unit_id"]
            attestations[unit_id] = temp / f"{unit_id}.attestation.json"
            raw_paths[unit_id] = temp / f"{unit_id}.raw.jsonl"
            write_json(attestations[unit_id], record)
            raw_paths[unit_id].write_bytes(raws[unit_id])
        return locals()

    def _prepare_command(self, fixture, destination: Path, *, units=None, effect_cap=None):
        paths = fixture["paths"]
        units = sorted(units or fixture["attestations"])
        repeated = []
        for unit_id in units:
            repeated += [
                "--attestation", f"{unit_id}={fixture['attestations'][unit_id]}",
                "--raw", f"{unit_id}={fixture['raw_paths'][unit_id]}",
            ]
        return [
            "python3", "-m", "evaluation.cli", "prepare-exact-request",
            "--repo", str(ROOT), "--product", str(paths["product"]),
            "--previous-product", str(paths["previous-product"]),
            "--previous-spec", str(paths["previous-spec"]),
            "--profiles", str(paths["profiles"]),
            "--total-cap", str(paths["total-cap"]),
            "--effect-cap", str(effect_cap or paths["effect-cap"]),
            "--mapping", str(paths["mapping"]), "--revealed-at", REVEALED_AT,
            "--review-brief", str(paths["review-brief"]),
            "--provider-binary", str(fixture["binary"]),
            "--external-role-config", str(fixture["role"]),
            "--hidden-oracle", str(fixture["oracle"]),
            "--exact-source", str(fixture["snapshot"]),
            "--destination", str(destination), *repeated,
        ]

    def test_cli_prepares_exact_only_request_equal_to_pure_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            fixture = self._exact_request_fixture(Path(raw))
            destination = Path(raw) / "request"
            completed = subprocess.run(
                self._prepare_command(fixture, destination), cwd=ROOT,
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            output = json.loads(completed.stdout)
            spec = json.loads((destination / "eval-spec.json").read_text())
            request = json.loads((destination / "authority-request.json").read_text())
            expected = exact_final_authority_proposal(
                root=ROOT, product=fixture["selected"],
                previous_product=fixture["baseline"],
                previous_spec=fixture["previous"], spec=spec,
                attestations=fixture["prior"], raw_streams={
                    unit_id: path.read_bytes() for unit_id, path in fixture["raw_paths"].items()
                }, holdout_mapping=fixture["mapping"],
                mapping_revealed_at=REVEALED_AT,
                total_cap=json.loads(fixture["paths"]["effect-cap"].read_text()),
            )
            self.assertEqual(request["proposal"], expected)
            self.assertEqual(request["selected_unit_ids"], ["exact-final"])
            self.assertFalse(request["canonical_approval_line"]["authoritative"])
            self.assertEqual(output["authority_request_sha256"], canonical_sha256(expected))
            self.assertFalse(fixture["marker"].exists())
            self.assertEqual(list((destination / "execution" / "raw").iterdir()), [])
            self.assertEqual(list(destination.rglob("auth.json")), [])
            self.assertEqual(os.stat(destination).st_mode & 0o777, 0o700)
            self.assertEqual(
                {path.name for path in destination.iterdir()},
                {
                    "authority-request.json", "effect-cap.json", "eval-spec.json",
                    "execution", "holdout-mapping.json", "host-contract.json",
                    "host-policy.json", "previous-eval-spec.json",
                    "previous-product.json", "private", "product.json",
                    "profiles.json", "review-brief.json", "total-cap.json",
                },
            )
            for path in destination.iterdir():
                self.assertEqual(os.stat(path).st_mode & 0o777, 0o700 if path.is_dir() else 0o600)

    def test_cli_exact_request_rejects_bad_prerequisites_caps_and_collisions(self):
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw); fixture = self._exact_request_fixture(temp)
            missing = sorted(fixture["attestations"])[:-1]
            full_cap = temp / "full-effect-cap.json"; write_json(full_cap, TOTAL_CAP)
            bad_raw = next(iter(fixture["raw_paths"].values()))
            original_raw = bad_raw.read_bytes(); bad_raw.write_bytes(original_raw + b"{}\n")
            tampered = subprocess.run(
                self._prepare_command(fixture, temp / "tampered"), cwd=ROOT,
                capture_output=True, text=True, check=False,
            )
            bad_raw.write_bytes(original_raw)
            failed_unit = next(iter(fixture["attestations"]))
            failed_path = fixture["attestations"][failed_unit]
            record = json.loads(failed_path.read_text())
            write_json(failed_path, reseal({**record, "verdict": "fail"}))
            failed = subprocess.run(
                self._prepare_command(fixture, temp / "failed"), cwd=ROOT,
                capture_output=True, text=True, check=False,
            )
            write_json(failed_path, record)
            collision = temp / "collision"; collision.mkdir()
            results = [
                subprocess.run(self._prepare_command(fixture, temp / "missing", units=missing), cwd=ROOT, capture_output=True, text=True, check=False),
                subprocess.run(self._prepare_command(fixture, temp / "full", effect_cap=full_cap), cwd=ROOT, capture_output=True, text=True, check=False),
                subprocess.run(self._prepare_command(fixture, collision), cwd=ROOT, capture_output=True, text=True, check=False),
                tampered, failed,
            ]
            self.assertTrue(all(result.returncode != 0 for result in results))
            self.assertTrue(all(not (temp / name).with_name((temp / name).name + ".staging").exists() for name in ("missing", "full", "tampered", "failed")))
    def test_fake_subprocess_raw_stream_verifies_end_to_end(self):
        selected, baseline, spec, _ = bundle()
        unit = next(item for item in spec["units"] if item["unit_id"] == "goal-divergence")
        payload = {
            "started_at": "2026-08-02T00:00:00Z", "frozen_at": "2026-08-02T00:00:10Z",
            "report": passing_report(unit),
            "usage": {"input_tokens": 10, "cached_input_tokens": 0, "cache_write_input_tokens": 0, "output_tokens": 2, "reasoning_output_tokens": 0},
        }
        completed = subprocess.run(
            ["python3", str(ROOT / "tests" / "fake_external_host.py")],
            input=json.dumps(payload), text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        raw = completed.stdout.encode()
        record = attestation_from_raw(
            root=ROOT, product=selected, spec=spec, unit_id=unit["unit_id"], raw=raw,
            host_metadata={key: payload[key] for key in ("started_at", "frozen_at")} | {"exit_code": 0, "timed_out": False},
            authority_sha256=SHA["a"],
        )
        self.assertEqual(record["verdict"], "pass")
        self.assertEqual(baseline["external_role_config_sha256"], selected["external_role_config_sha256"])

    def test_cli_materializes_from_versioned_production_inputs(self):
        selected, baseline, spec, blind_mapping = bundle()
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            values = {
                "product": selected, "previous": baseline, "profiles": PROFILES,
                "cap": TOTAL_CAP, "mapping": blind_mapping, "brief": REVIEW_BRIEF,
                "host": HOST_CONTRACT,
            }
            paths = {}
            for name, value in values.items():
                paths[name] = temp / f"{name}.json"
                write_json(paths[name], value)
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "materialize", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--profiles", str(paths["profiles"]), "--total-cap", str(paths["cap"]),
                    "--mapping", str(paths["mapping"]), "--review-brief", str(paths["brief"]),
                    "--host-contract", str(paths["host"]),
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), spec)

    def test_cli_verifies_records_only_with_fixed_host_raw(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(selected, baseline, spec)
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            fixed = {"product": selected, "previous": baseline, "spec": spec, "mapping": blind_mapping}
            paths = {}
            for name, value in fixed.items():
                paths[name] = temp / f"{name}.json"
                write_json(paths[name], value)
            repeated = []
            for index, record in enumerate(records):
                unit_id = record["unit_id"]
                attestation_path = temp / f"attestation-{index}.json"
                raw_path = temp / f"raw-{index}.jsonl"
                write_json(attestation_path, record)
                raw_path.write_bytes(raws[unit_id])
                repeated.extend(["--attestation", str(attestation_path), "--raw", f"{unit_id}={raw_path}"])
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--mapping", str(paths["mapping"]),
                    "--revealed-at", REVEALED_AT,
                    *repeated,
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["verified"])
        self.assertNotIn("certified", result)

    def test_cli_rejects_legacy_host_flags(self):
        selected, baseline, spec, blind_mapping = bundle()
        records, raws = attest_all(selected, baseline, spec)
        record = records[0]
        unit_id = record["unit_id"]
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            paths = {name: temp / f"{name}.json" for name in ("product", "previous", "spec", "mapping", "attestation", "legacy")}
            for name, value in (("product", selected), ("previous", baseline), ("spec", spec), ("mapping", blind_mapping), ("attestation", record), ("legacy", {})):
                write_json(paths[name], value)
            raw_path = temp / "raw.jsonl"
            raw_path.write_bytes(raws[unit_id])
            old_data_flag = "--" + "pro" + "of"
            old_command_flag = old_data_flag + "-ver" + "ifier-command"
            completed = subprocess.run(
                [
                    "python3", "-m", "evaluation.cli", "verify", "--repo", str(ROOT),
                    "--product", str(paths["product"]), "--previous-product", str(paths["previous"]),
                    "--spec", str(paths["spec"]), "--attestation", str(paths["attestation"]),
                    "--raw", f"{unit_id}={raw_path}", old_data_flag, f"{unit_id}={paths['legacy']}",
                    old_command_flag, "/usr/bin/true",
                ], cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unrecognized arguments", completed.stderr)


if __name__ == "__main__":
    unittest.main()
